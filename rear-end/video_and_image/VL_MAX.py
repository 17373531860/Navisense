from openai import OpenAI
import os
import sys
import base64
import dashscope 
import time
from dashscope.audio.tts.speech_synthesizer import SpeechSynthesizer

# 从命令行参数获取图片路径
if len(sys.argv) < 2:
    raise ValueError("未提供图片路径")
image_path = sys.argv[1]
print(f"接收到的图片路径: {image_path}")

# 读取并编码图片为 Base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 编码图片
base64_image = encode_image(image_path)

# 调用 OpenAI 接口
client = OpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-max-latest",
    messages=[
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a helpful assistant."}]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                {"type": "text", "text": "图中描绘的是什么景象?"},
            ],
        }
    ],
)

vl_max_text = completion.choices[0].message.content

# === 模拟逐字打印 ===
print("分析结果：", end='', flush=True)
for char in vl_max_text:
    print(char, end='', flush=True)
    time.sleep(0.1)
print()

# === 保存文本结果 ===
output_file = "vl_max_output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(vl_max_text)
print(f"结果已保存到 {output_file}")

# === TTS 合成音频 ===
print("正在将分析结果转换为语音...")

text_to_speak = vl_max_text[:500]
tts = SpeechSynthesizer()
tts_response = tts.call(
    model="sambert-zhichu-v1",
    text=text_to_speak,
    sample_rate=24000,
    format="wav"
)

audio_data = tts_response.get_audio_data()
if audio_data:
    audio_output_dir = "./audio_cache"
    os.makedirs(audio_output_dir, exist_ok=True)
    audio_output_path = os.path.join(audio_output_dir, "vl_max.wav")
    with open(audio_output_path, "wb") as f:
        f.write(audio_data)
    print(f"语音文件已保存为 {audio_output_path}")
else:
    print("TTS 合成失败：未返回音频数据")
