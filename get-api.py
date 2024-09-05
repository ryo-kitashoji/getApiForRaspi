import requests
import RPi.GPIO as GPIO
import time

# GPIOの設定
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

PUSH_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUSH_PIN, GPIO.OUT, initial=GPIO.LOW)

url = "http://192.168.10.102:8000/nyoui"

def check_level():
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        data = response.json()
        return data.get("level", 0)
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return 0
        
def check_score():
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        data = response.json()
        return data.get("total_score", 0)
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return 0

def control_led(level):
    if level >= 8:
        GPIO.output(LED_PIN, GPIO.HIGH)  # LEDを点灯
    else:
        GPIO.output(LED_PIN, GPIO.LOW)   # LEDを消灯

def control_push(score):
    if score >= 100:
        GPIO.output(PUSH_PIN, GPIO.HIGH)  # rocket push
    else:
        GPIO.output(PUSH_PIN, GPIO.LOW)   # rocket push

try:
    while True:
        level = check_level()
        control_led(level)
        score = check_score()
        control_push(score)
        time.sleep(1)  # 1秒ごとにスコアをチェック
except KeyboardInterrupt:
    print("Program interrupted")
finally:
    GPIO.cleanup()  # GPIOのクリーンアップ
