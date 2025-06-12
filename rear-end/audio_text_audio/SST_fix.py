import os
from pydub import AudioSegment
import speech_recognition as sr

def stt_process(filename: str) -> str:
    """
    使用 speech_recognition 识别本地音频文件。
    自动将音频转为标准 PCM WAV 格式（兼容 Google STT）。
    :param filename: 存放在 ./audio_cache/ 下的音频文件名
    :return: 转写文本
    """
    original_path = os.path.join("audio_cache", filename)
    if not os.path.exists(original_path):
        print(f"文件不存在：{original_path}")
        return ""

    # 生成临时转换后的文件名
    temp_wav_path = original_path.replace(".wav", "_converted.wav")
    try:
        # 转换为标准 PCM WAV 格式
        audio = AudioSegment.from_file(original_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(temp_wav_path, format="wav", parameters=["-acodec", "pcm_s16le"])
    except Exception as e:
        print(f"❌ 音频转换失败：{e}")
        return ""

    # 使用 speech_recognition 进行识别
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_wav_path) as source:
            print(f"正在识别音频文件：{temp_wav_path}")
            audio = recognizer.record(source)
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
    finally:
        # 清理临时转换文件
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
