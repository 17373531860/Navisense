import dashscope
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from map.map import map_text

# 读取 VL_MAX.py 的输出结果
vl_max_output_file = "vl_max_output.txt"
if not os.path.exists(vl_max_output_file):
    raise FileNotFoundError(f"未找到 {vl_max_output_file}，请检查 VL_MAX.py 是否正确运行")
with open(vl_max_output_file, "r", encoding="utf-8") as f:
    vl_max_text = f.read().strip()

# 两段文本变量
text1 = map_text
text2 = vl_max_text

audio1 = None
audio2 = None

response1 = dashscope.TextToSpeech.call(
    model="sambert-zhichu-v1",
    text=text1,
    sample_rate=24000,
    format="wav"
)
if response1.get("audio"):
    audio1 = response1["audio"]
    with open("map.wav", "wb") as f:
        f.write(audio1)
    print("第一段语音已保存为 map.wav")
else:
    print("TTS 失败：", response1)

response2 = dashscope.TextToSpeech.call(
    model="sambert-zhichu-v1",
    text=text2,
    sample_rate=24000,
    format="wav"
)
if response2.get("audio"):
    audio2 = response2["audio"]
    with open("vl_max.wav", "wb") as f:
        f.write(audio2)
    print("第二段语音已保存为 vl_max.wav")
else:
    print("TTS 失败：", response2)

# audio1 和 audio2 即为两段文本各自的音频变量