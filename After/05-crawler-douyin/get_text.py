# encoding: utf8
# author: wrfeng
# contact: feng@forchange.tech
# datetime:2022/2/11 11:14 上午

"""
文件说明：

"""
import os
import time

import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(subscription="221d02def2c4471cb296583f95a3186b", region="southeastasia")


def save_text(file, text):
    print(text)
    with open(file, 'a') as f:
        f.write(text)


def audio_to_text(file):
    speech_config.speech_recognition_language = "zh-CN"  # 语音识别
    done = False

    def stop_cb(evt):
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    save_text(file.replace('wav', 'txt'), "")  # 清空文本
    audio_input = speechsdk.AudioConfig(filename=file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
    speech_recognizer.recognized.connect(lambda evt: save_text(file.replace('wav', 'txt'), evt.result.text))
    speech_recognizer.start_continuous_recognition()
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    while not done:
        time.sleep(.5)
    speech_recognizer.stop_continuous_recognition()


if __name__ == '__main__':
    file = input("请输入视频或音频文件路径：")
    print(file)
    file_info = file.split(".")
    if file_info[-1] != 'wav':
        print("开始提取音频文件")
        os.system("./ffmpeg -y -i {} -f wav {}".format(file, file.replace(file_info[-1], 'wav')))
        file = file.replace(file_info[-1], 'wav')
    print("开始转换成文本")
    audio_to_text(file)
