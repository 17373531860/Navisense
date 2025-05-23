# vl_analyzer.py

import os
import base64
from openai import OpenAI


def encode_image(image_path):
    """将本地图片编码为 Base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_qwen_vl_max(image_path: str) -> str:
    """
    使用 Qwen-VL-Max 或 QVQ 模型分析本地图片内容，并支持流式输出。

    参数:
        image_path (str): 本地图片路径

    返回:
        str: 模型生成的答案文本
    """
    client = OpenAI(
        api_key= "sk-9073d9adbcf346debc161e2c2735c422",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1 "
    )

    try:
        base64_image = encode_image(image_path)

        # 根据扩展名判断 MIME 类型
        if image_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif image_path.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"
        elif image_path.lower().endswith(".webp"):
            mime_type = "image/webp"
        else:
            raise ValueError("不支持的图片格式")

        data_uri = f"data:{mime_type};base64,{base64_image}"

        print("🧠 正在调用 Qwen-VL 模型进行图像理解...")

        completion = client.chat.completions.create(
            model="qvq-max",  # 可替换为 qwen-vl-max-latest 等
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri}
                        },
                        {"type": "text", "text": "请描述这张图片的内容。"}
                    ]
                }
            ],
            stream=True,
        )

        reasoning_content = ""
        answer_content = ""
        is_answering = False

        print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 输出思考过程
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                print(delta.reasoning_content, end='', flush=True)
                reasoning_content += delta.reasoning_content

            # 开始正式回答
            if delta.content:
                if not is_answering:
                    print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                    is_answering = True
                print(delta.content, end='', flush=True)
                answer_content += delta.content

        print("\n" + "=" * 50)

        return answer_content.strip()

    except Exception as e:
        print(f"\n❌ 图像分析失败：{e}")
        return f"[错误] 图像分析失败: {str(e)}"