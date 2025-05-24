from openai import OpenAI
import os
import sys
import base64
import dashscope 
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
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-vl-max-latest",  # 此处以 qwen-vl-max-latest 为例，可按需更换模型名称
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
                    # 需要注意，传入 Base64，图像格式（即 image/{format}）需要与支持的图片列表中的 Content Type 保持一致
                    # PNG 图像：  f"data:image/png;base64,{base64_image}"
                    # JPEG 图像： f"data:image/jpeg;base64,{base64_image}"
                    # WEBP 图像： f"data:image/webp;base64,{base64_image}"
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                {"type": "text", "text": "图中描绘的是什么景象?"},
            ],
        }
    ],
)
# print(completion.choices[0].message.content)
# vl_max_text = completion.choices[0].message.content
# print(vl_max_text)

# # 将结果保存到文件
# output_file = "vl_max_output.txt"
# with open(output_file, "w", encoding="utf-8") as f:
#     f.write(vl_max_text)
# print(f"结果已保存到 {output_file}")
vl_max_text = completion.choices[0].message.content
print("分析结果：", vl_max_text)

# === 4. 保存文本结果 ===
output_file = "vl_max_output.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(vl_max_text)
print(f"结果已保存到 {output_file}")

# === 5. 使用 DashScope TTS 合成音频 ===
print("正在将分析结果转换为语音...")

# 防止文本过长，限制前 500 字以内
text_to_speak = vl_max_text[:500]

# 创建 TTS 合成器并调用
tts = SpeechSynthesizer()
tts_response = tts.call(
    model="sambert-zhichu-v1",
    text=text_to_speak,
    sample_rate=24000,
    format="wav"
)

# 尝试获取音频数据
audio_data = tts_response.get_audio_data()
if audio_data:
    # 保存到指定目录
    audio_output_dir = "./audio_cache"
    os.makedirs(audio_output_dir, exist_ok=True)
    audio_output_path = os.path.join(audio_output_dir, "vl_max.wav")
    
    with open(audio_output_path, "wb") as f:
        f.write(audio_data)
    print(f"语音文件已保存为 {audio_output_path}")
else:
    print("TTS 合成失败：未返回音频数据")