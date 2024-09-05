#!/usr/bin/env python3
import time
import requests
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color
import argparse

# LEDストリップの設定
LED_COUNT = 16        # LEDピクセルの数
LED_PIN = 21          # GPIOピン番号
LED_FREQ_HZ = 800000  # LED信号周波数
LED_DMA = 10          # DMAチャネル
LED_BRIGHTNESS = 255  # 輝度
LED_INVERT = False    # 信号の反転
LED_CHANNEL = 0       # GPIOチャネル

# PUSH_PIN = [12, 13]

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
# GPIO.setup(PUSH_PIN, GPIO.OUT, initial=GPIO.LOW)

url = "http://192.168.10.102:8000/nyoui"

def check_score():
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        data = response.json()
        return data.get("total_score", 0)
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return 0

def interpolate_color(score):
    """スコアに基づいて色を補間する関数"""
    # スコアに応じて色を補間
    if score <= 50:
        # 緑から黄色に補間
        r = int(255 * (score / 50))  # 0から255に線形補間
        g = 255
        b = 0
    else:
        # 黄色から赤に補間
        r = 255
        g = int(255 * (1 - (score - 50) / 50))  # 255から0に線形補間
        b = 0
    
    return Color(r, g, b)

def control_push(score):
    # Pushデバイスの制御はスコアに応じて実施
    if score >= 100:
        GPIO.output(PUSH_PIN, GPIO.HIGH)  # Pushデバイスをオン
    else:
        GPIO.output(PUSH_PIN, GPIO.LOW)   # Pushデバイスをオフ

def chase_color(strip, color, wait_ms=50, iterations=10):
    """LEDで色のチェイスアニメーションを実行する関数"""
    for j in range(iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            strip.setPixelColor(i, Color(0, 0, 0))  # 消灯
        # 最後のLEDを再び点灯させて、チェイスの動きを強調する
        strip.setPixelColor(strip.numPixels() - 1, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # NeoPixelオブジェクトの作成と初期化
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            # APIからデータを取得し、スコアに応じた色を補間
            score = check_score()
            color = interpolate_color(score)
            # control_push(score)

            # スコアに応じたLEDのチェイスアニメーション
            print(f'Score: {score}, Color: {color}')
            chase_color(strip, color)

            time.sleep(1)  # 1秒ごとにスコアをチェック

    except KeyboardInterrupt:
        print("Program interrupted")
        if args.clear:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(0, 0, 0))  # 全てのLEDを消灯
            strip.show()
            time.sleep(5)  # 消灯を確認するために5秒待機
    finally:
        GPIO.cleanup()  # GPIOのクリーンアップ
