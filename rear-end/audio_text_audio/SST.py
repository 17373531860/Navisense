# # audio_text_audio/SST.py

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
import time
import requests
from requests.exceptions import SSLError, RequestException

# 从环境变量或配置中读取
API_KEY = "sk-9073d9adbcf346debc161e2c2735c422"
# HTTP ASR 接口地址（请根据实际文档替换）
ASR_ENDPOINT = "https://api.dashscope.com/v1/asr"

def stt_process(filename: str) -> str:
    """
    使用 DashScope HTTP REST 接口进行语音识别，带重试与 SSL 验证跳过机制。
    :param filename: 存放在 ./audio_cache/ 下的 wav 音频文件
    :return: 转写文本
    """
    local_path = os.path.join("audio_cache", filename)
    if not os.path.exists(local_path):
        print(f"文件不存在：{local_path}")
        return ""

    print(f"开始通过 HTTP 接口识别：{local_path}")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {"model": "paraformer-realtime-v1", "sample_rate": 16000}

    # 重试配置
    max_retries = 3
    backoff = [1, 2, 4]  # 秒

    for attempt in range(1, max_retries + 1):
        try:
            with open(local_path, "rb") as f:
                files = {"file": (filename, f, "audio/wav")}
                resp = requests.post(
                    ASR_ENDPOINT,
                    headers=headers,
                    params=params,
                    files=files,
                    timeout=30,
                    verify=True  # 默认验证证书
                )
            resp.raise_for_status()
            data = resp.json()
            text = data.get("text", "").strip()
            print(f"识别成功（第 {attempt} 次）：{text}")
            print("-" * 40)
            return text

        except SSLError as e:
            print(f"[SSL 错误 第{attempt}次] {e}")
            if attempt < max_retries:
                wait = backoff[attempt - 1]
                print(f"等待 {wait}s 后重试…")
                time.sleep(wait)
                continue
            else:
                print("最后一次尝试：跳过 SSL 验证")
                try:
                    with open(local_path, "rb") as f:
                        files = {"file": (filename, f, "audio/wav")}
                        resp = requests.post(
                            ASR_ENDPOINT,
                            headers=headers,
                            params=params,
                            files=files,
                            timeout=30,
                            verify=False  # 跳过 SSL 验证
                        )
                    resp.raise_for_status()
                    data = resp.json()
                    text = data.get("text", "").strip()
                    print(f"跳过验证后识别成功：{text}")
                    print("-" * 40)
                    return text
                except Exception as e2:
                    print(f"跳过验证后也失败：{e2}")
                    return ""

        except RequestException as e:
            # 包括网络、超时、HTTP 错误等
            print(f"[网络/HTTP 错误 第{attempt}次] {e}")
            if attempt < max_retries:
                wait = backoff[attempt - 1]
                print(f"等待 {wait}s 后重试…")
                time.sleep(wait)
                continue
            else:
                print("已达最大重试次数，放弃识别。")
                return ""

    # 如果循环结束，返回空
    return ""
