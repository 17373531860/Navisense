# vl_analyzer.py

from openai import OpenAI

def analyze_image_with_qwen_vl_max(image_url: str) -> str:
    """
    使用 Qwen-VL-Max 或 QVQ 模型分析远程图片，并支持流式输出。

    参数:
        image_url (str): 公网可访问的图片 URL（例如通过 ngrok 映射的地址）

    返回:
        str: 模型生成的答案文本
    """
    client = OpenAI(
        api_key="sk-9073d9adbcf346debc161e2c2735c422",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1 "
    )

    try:
        completion = client.chat.completions.create(
            model="qvq-max",  # 可替换为 qwen-vl-max-latest 等
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                        {"type": "text", "text": "请描述这张图片的内容。"}
                    ]
                }
            ],
            stream=True,
        )

        answer_content = ""
        is_answering = False

        print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

        for chunk in completion:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                print(delta.reasoning_content, end='', flush=True)

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