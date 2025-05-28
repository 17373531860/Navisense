# audio_text_audio/SST.py

# from dashscope.audio.asr import Recognition
# import dashscope
# import time

# dashscope.api_key = "sk-9073d9adbcf346debc161e2c2735c422"  # 替换为你的 API Key

# # 自定义回调函数
# def on_event(message):
#     if message and hasattr(message.output, 'text'):
#         on_event.text += message.output.text

# on_event.text = ""


# def stt_process(filename):
#     """
#     使用 DashScope v1.23.3 实现语音识别（通过 file_url）
#     """
#     audio_url = f"http://127.0.0.1:8000/get-audio/{filename}"
#     print(f"处理音频文件：{filename}，URL：{audio_url}")

#     on_event.text = ""  # 清空上一次结果

#     try:
#         recognizer = Recognition(
#             model='paraformer-realtime-v1',
#             sample_rate=16000,
#             format='wav',
#             callback=on_event
#         )
#         recognizer.call(file_url=audio_url)  # ✅ 正确参数名是 file_url！

#         # 轮询等待识别结果
#         start_time = time.time()
#         while not on_event.text:
#             time.sleep(0.5)
#             if time.time() - start_time > 10:
#                 raise TimeoutError("语音识别超时")
#     except Exception as e:
#         print(f"调用 DashScope 模型时发生异常：{e}")
#         return ""

#     stt_text = on_event.text.strip()
#     print(f"音频 {filename} 的转写结果：\n{stt_text}")
#     print("-" * 40)
#     return stt_text
# audio_text_audio/SST.py

import os
import speech_recognition as sr

def stt_process(filename: str) -> str:
    """
    使用 speech_recognition 识别本地 wav 文件（Google API，需联网）。
    :param filename: 存放在 ./audio_cache/ 下的 wav 音频文件
    :return: 转写文本
    """
    local_path = os.path.join("audio_cache", filename)
    if not os.path.exists(local_path):
        print(f"文件不存在：{local_path}")
        return ""

    recognizer = sr.Recognizer()
    with sr.AudioFile(local_path) as source:
        print(f"正在识别音频文件：{local_path}")
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language="zh-CN")
        print(f"识别结果：{text}")
        print("-" * 40)
        return text
    except sr.UnknownValueError:
        print("❌ 无法理解音频内容")
        print("-" * 40)
        return ""
    except sr.RequestError as e:
        print(f"❌ 请求失败: {e}")
        print("-" * 40)
        return ""
