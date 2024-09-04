import requests
import RPi.GPIO as GPIO
import time

# GPIOの設定
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

def check_score():
    url = "http://0.0.0.0:8000"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        data = response.json()
        return data.get("total-score", 0)
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return 0

def control_led(score):
    if score > 80:
        GPIO.output(LED_PIN, GPIO.HIGH)  # LEDを点灯
    else:
        GPIO.output(LED_PIN, GPIO.LOW)   # LEDを消灯

try:
    while True:
        score = check_score()
        control_led(score)
        time.sleep(10)  # 10秒ごとにスコアをチェック
except KeyboardInterrupt:
    print("Program interrupted")
finally:
    GPIO.cleanup()  # GPIOのクリーンアップ
