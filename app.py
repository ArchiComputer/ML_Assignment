from flask import Flask, render_template, jsonify
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Flask 앱을 생성합니다.
app = Flask(__name__)

# Open-Meteo API 클라이언트 설정
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/weather_data')
def get_weather_data():
    # API 요청을 보내서 날씨 데이터를 가져옵니다.
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 37.566,
        "longitude": 126.9784,
        "start_date": "2022-01-01",
        "end_date": "2022-12-31",
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "rain", "snowfall", "cloud_cover",
                   "wind_speed_10m", "wind_speed_100m"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # 첫 번째 위치의 데이터를 처리합니다.
    response = responses[0]

    # hourly 데이터 처리
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s"),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ).tolist(),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy().tolist(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy().tolist(),
        "dew_point_2m": hourly.Variables(2).ValuesAsNumpy().tolist(),
        "rain": hourly.Variables(3).ValuesAsNumpy().tolist(),
        "snowfall": hourly.Variables(4).ValuesAsNumpy().tolist(),
        "cloud_cover": hourly.Variables(5).ValuesAsNumpy().tolist(),
        "wind_speed_10m": hourly.Variables(6).ValuesAsNumpy().tolist(),
        "wind_speed_100m": hourly.Variables(7).ValuesAsNumpy().tolist(),
    }

    # JSON 형식으로 데이터 반환
    return jsonify(hourly_data)


# 앱을 실행합니다.
if __name__ == '__main__':
    app.run(debug=True)



