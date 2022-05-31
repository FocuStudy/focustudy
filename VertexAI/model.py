from google.cloud import storage
import os
import json
import subprocess
import time
import re
def modelcon():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="C:/program1/capstone/video_intelligence/key.json"
    print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    bucket_name = 'focustudy-result'    # 서비스 계정 생성한 bucket 이름 입력
    source_file_name = '../student_video.mp4'  # GCP에 업로드할 파일 절대경로
    destination_blob_name = 'student_video'    # 업로드할 파일을 GCP에 저장할 때의 이름

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name+'.mp4') # 저장 파일 명 세팅
    blob.upload_from_filename(source_file_name) # 영상 파일 업로드

    csv_file = open("./student_video.csv", "w")
    csv_file.write('gs://focustudy-result/student_video.mp4'+',0,inf')
    csv_file.close()
    blob = bucket.blob(destination_blob_name+'.csv') #저장 파일 명 세팅
    blob.upload_from_filename('./student_video.csv')


    request_data = {
      "inputConfig": {
        "gcsSource": {
          "inputUris": [""]
        }
      },
      "outputConfig": {
        "gcsDestination": {
          "outputUriPrefix": ""
        }
      },
      "params": {
        "1s_interval_classification" : "true"
      }
    }
    request_gcp_csv = ["gs://focustudy-result/student_video.csv"]
    response_uri = "gs://focustudy-result/predict_result/"
    request_data["inputConfig"]["gcsSource"]["inputUris"] = request_gcp_csv
    request_data["outputConfig"]["gcsDestination"]["outputUriPrefix"] = response_uri

    file_path = "./request.json"
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(request_data, file)

    key=subprocess.check_output('gcloud auth application-default print-access-token', shell=True)
    key=str(key)[2:-5]
    req='curl -L -X POST -H "Content-Type: application/json" -H "Authorization: Bearer {}" https://automl.googleapis.com/v1beta1/projects/143439614880/locations/us-central1/models/VCN6756804616916041728:batchPredict -d @request.json'.format(key)
    req_out = subprocess.check_output(req, shell=True)

    project_info = re.search('"name": "(.+?)"', str(req_out)).group(1)
    req2 = 'curl -L -X GET \
    -H "Authorization: Bearer "{} \
    "https://automl.googleapis.com/v1beta1/{}"'.format(key, project_info)  #예측 상태 체크 / 예측 완료시 예측 정보 리턴
    while True:
        req_out2 = subprocess.check_output(req2, shell=True)
        if re.search('"gcsOutputDirectory": "(.+?)"', str(req_out2)) == None:
            time.sleep(90)
            continue
        else:
            dir_name = re.search('"gcsOutputDirectory": "(.+?)"', str(req_out2)).group(1)
            break
    print(dir_name)
    dir_name='gs://focustudy-result/predict_result/prediction-untitled_16510289_20220427022643-2022-05-29T02:40:31.977477Z'
    bucket_name = 'focustudy-result'    # 서비스 계정 생성한 bucket 이름 입력
    # source_blob_name = 'predict_result/model_result/{}/student_video_1.json'.format(dir_name)    # GCP에 저장되어 있는 파일 명
    source_blob_name=dir_name[22:]+'/student_video_1.json'
    destination_file_name = '../data/vertex_json/model_result.json'  # 다운받을 파일을 저장할 경로("local/path/to/file")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)
modelcon()
