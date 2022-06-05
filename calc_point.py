import collections
import json

import cv2
import numpy as np
from CV.gaze_tracking.gaze_tracking import GazeTracking
import time
import csv

face_cascade = cv2.CascadeClassifier('./CV/face_recognition/haarcascade_frontface.xml')
video_path = 'student_video.mp4'
cap = cv2.VideoCapture(video_path)
gaze = GazeTracking()
prev_x, prev_y, cur_x, cur_y = 0, 0, 0, 0

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.05, 5)
    if len(faces):
        prev_x, prev_y = faces[0][0], faces[0][1]
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.05, 5)
        if len(faces):
            cur_x, cur_y = faces[0][0], faces[0][1]
            break
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

move = 0
prev = abs(prev_x - cur_x) + abs(prev_y - cur_y)
prev_move = abs(prev_x - cur_x) + abs(prev_y - cur_y)
move_q = collections.deque()
move_window_size = 4
min_movement = 10000
gaze_frame_cnt = 1
gaze_center = 1
get_point_time = time.time()
cv_point = []


def get_point():
    # movement
    global move
    global prev
    global min_movement
    global get_point_time
    move_point = 0

    move_q.append(move)

    if len(move_q) == move_window_size:
        move = move_q[0] * 0.1
        move += move_q[1] * 0.1
        move += move_q[2] * 0.3
        move += move_q[3] * 0.5
        move_q.popleft()

    # 여기가 파라미터 조절하는 부분
    # 점수가 너무 높게 나오면 0.3을 줄이고
    # 점수가 낮게 나오면 0.3보다 큰 값을 주면 됨
    if move > (prev * (1.43 + 0.3)) or move > min_movement * 5:
        move_point = 0
    elif move > (prev * (1.22 + 0.3)):
        move_point = 1
    else:
        move_point = 2

    min_movement = min(min_movement, move)
    prev = move
    move = 0
    gaze_point = 0

    # gaze
    global gaze_frame_cnt
    global gaze_center
    calc_gaze = gaze_center / gaze_frame_cnt

    gaze_frame_cnt = 1
    gaze_center = 1

    # 여기가 파라미터 조절하는 부분
    # 점수가 너무 높게 나오면 0.2를 줄이고
    # 점수가 낮게 나오면 0.2보다 큰 값을 주면 됨
    # 0.828, 0.719, 0.582
    if calc_gaze > (0.828 - 0.2):
        gaze_point += 2
    elif calc_gaze > (0.719 - 0.2):
        gaze_point += 1
    else:  # 0.582
        gaze_point += 0

    cv_point.append(move_point + gaze_point + 1)


fps = int(cap.get(cv2.CAP_PROP_FPS))
cur_frame_cnt = 0
calc_cnt = 1

while True:

    if cur_frame_cnt >= fps * 5:
        cap.set(cv2.CAP_PROP_POS_FRAMES, calc_cnt * fps * 5)
        calc_cnt += 1
        cur_frame_cnt = 0
        get_point()

    ret, frame = cap.read()
    cap.read()
    cap.read()
    cap.read()
    cap.read()

    cur_frame_cnt += 5

    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.05, 5)
    if len(faces):
        for (x, y, w, h) in faces:
            cur_x, cur_y = x, y
            prev_move = abs(prev_x - cur_x) + abs(prev_y - cur_y)
            move += abs(prev_x - cur_x) + abs(prev_y - cur_y)
            prev_x, prev_y = cur_x, cur_y
    else:
        move += prev_move

    gaze.refresh(frame)

    if gaze.is_left():
        gaze_frame_cnt += 1

    if gaze.is_right():
        gaze_frame_cnt += 1

    elif gaze.is_center():
        gaze_frame_cnt += 1
        gaze_center += 1

get_point()

def parse_json(f):
    file = open(f)
    jsonString = json.load(file)
    con_data = []
    if len(jsonString.get("one_second_interval_classification_annotations")[0]['frames']) == len(
            jsonString.get("one_second_interval_classification_annotations")[1]['frames']):
        for i in range(2):
            if jsonString.get("one_second_interval_classification_annotations")[i]['annotation_spec']['description'] == '2':
                data = jsonString.get("one_second_interval_classification_annotations")[i]['frames']
                con_data = [data[j]['confidence'] * 100 for j in range(len(data))]
                # print(len(con_data))
                con_data = np.array([np.array(con_data[i:i + 5]).mean() for i in range(0, len(con_data), 5)])

                return con_data
    else:
        for i in range(2):
            if jsonString.get("one_second_interval_classification_annotations")[i]['annotation_spec']['description'] == '0':
                data = jsonString.get("one_second_interval_classification_annotations")[i]['frames']
                zero_data = [[data[j]['time_offset']['seconds'], round(100 - data[j]['confidence'] * 100, 2)] for j in
                             range(len(data))]  # 0점에 대한 데이터의 confidence 값을 2점에 대한 값으로 변경(100-confidence)한 후 2자리 반올림
            else:
                data = jsonString.get("one_second_interval_classification_annotations")[i]['frames']
                two_data = [[data[j]['time_offset']['seconds'], round(data[j]['confidence'] * 100, 2)] for j in
                            range(len(data))]
                # con_data.append(json_data)
        con_data = zero_data + two_data
        print(len(con_data))
        con_data = sorted(con_data, key=lambda x: x[0])
        con_data = np.array(con_data)[:, 1]
        con_data = np.array([np.array(con_data[i:i + 5]).mean() for i in range(0, len(con_data), 5)])
        return con_data


ml_point = parse_json('data/vertex_json/model_result.json')

csv_writer = csv.writer(open('data/point/{}.csv'.format(video_path[:-4]), 'w', encoding='utf-8-sig', newline=""))
csv_writer.writerow(['time', 'cv', 'ml', 'blend'])
csv_writer.writerow(['0','0','0'])

end = 0
for t in range(len(cv_point)):
    try:
        csv_writer.writerow([(t * 5)+5, cv_point[end] * 20, ml_point[t]])
        end += 1
    except: break