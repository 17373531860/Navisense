from openai import OpenAI
import os
import sys
import base64


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
print(completion.choices[0].message.content)