import streamlit as st
import pandas as pd
import numpy as np
import time
import altair as alt
from datetime import datetime
from PIL import Image
import result

# calc_point에서 저장한 최종 점수 계산 경로
result.createpdf('data/point/point_csv.csv')
point = pd.read_csv('data/point/point_csv.csv')
point = point.set_index('time')
point['blend'] = point['cv'] * 0.3 + point['ml'] * 0.7
left = pd.DataFrame(point, columns=['cv', 'ml'])  # 왼쪽에 그려지는 그래프, cv, ml 결과 같이 보여주는
right = pd.DataFrame(point, columns=['blend'])
left_melt = left.reset_index().melt('time', var_name='category', value_name='y')
left_melt = left_melt.sort_values('time')
right_melt = right.reset_index().melt('time', var_name='category', value_name='y')
right_melt = right_melt.sort_values('time')

logo = Image.open('logo.png')
st.set_page_config(layout="wide")
st.sidebar.image(logo)
name = st.sidebar.selectbox('Student', ['', '이대성', '한재민', '박준영'],
                            format_func=lambda x: 'Select Student' if x == '' else x)

if name:
    subject = st.sidebar.selectbox('Subject', ['', '캡스톤 디자인 1', '캡스톤디자인 2', '알고리즘', '자료구조'],
                                   format_func=lambda x: 'Select Subject' if x == '' else x)
    if subject:
        date = st.sidebar.date_input('Class Date', datetime(2022, 6, 9))
        if date.timetuple() != datetime(2022, 6, 9).timetuple():
            btn = st.sidebar.button('Start FocuStudy')
            if btn:
                # 만약 재민이 영상이 클릭 됐을 경우
                # if name == '한재민':
                #     video_file = open('재민이 영상 파일 경로.mp4', 'rb')
                #     ~~~
                # 준영이일 경우
                # elif name == '박준영':
                #     video_file = ~~

                video_file = open('student_video.mp4', 'rb')  # 이 부분이 영상 파일 (mp4일 것)
                video_bytes = video_file.read()
                _, video_layout, _ = st.columns((1, 2, 1))
                graph_layout = st.columns(2)

                with video_layout:
                    vid = st.video(video_bytes)

                l_start = 0
                l_end = 0
                r_start = 0
                r_end = 0
                left_chart = alt.Chart(left_melt[l_start:l_end]).mark_line(interpolate='basis').encode(
                    alt.X('time', title='sec'),
                    alt.Y('y', title='Point'),
                    color='category:N'
                ).properties(
                    title='CV, ML 분석 이해도 점수')  # 이런 부분은 화면에 나타나는 부분이라 바꿔도 됨

                right_chart = alt.Chart(right_melt[r_start:r_end]).mark_line(interpolate='basis').encode(
                    alt.X('time', title='sec'),
                    alt.Y('y', title='Point'),
                ).properties(
                    title='최종 이해도 점수')

                with graph_layout[0]:
                    left_graph = st.altair_chart(left_chart, use_container_width=True)
                with graph_layout[1]:
                    right_graph = st.altair_chart(right_chart, use_container_width=True)

                prev = time.time()
                while True:
                    if r_end > len(point):
                        break

                    if time.time() - prev >= 4.995:
                        # print(time.time() - prev) <- 필요하면 출력해보기
                        # 그래프 5초마다 갱신하는 부분
                        left_chart = alt.Chart(left_melt[l_start:l_end]).mark_line(interpolate='basis').encode(
                            alt.X('time', title='sec'),
                            alt.Y('y', title='Point'),
                            color='category:N'
                        ).properties(
                            title='CV, ML 분석 이해도 점수')

                        right_chart = alt.Chart(right_melt[r_start:r_end]).mark_line(interpolate='basis').encode(
                            alt.X('time', title='sec'),
                            alt.Y('y', title='Point'),
                        ).properties(
                            title='최종 이해도 점수')

                        left_graph.altair_chart(left_chart, use_container_width=True)
                        right_graph.altair_chart(right_chart, use_container_width=True)

                        r_end += 1
                        if 10 < r_end:
                            r_start += 1

                        l_end += 2
                        if 20 < l_end:
                            l_start += 2
                        prev = time.time()

                # 영상 재생이 끝나면 3초 후에 전체 결과 한번에 보여줌
                time.sleep(3)
                left_graph.altair_chart(left, use_container_width=True)
                right_graph.altair_chart(right, use_container_width=True)
