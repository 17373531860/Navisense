from http import HTTPStatus
from dashscope import Application
import time

map_text = ""  # 全局缓存结果

def generate_map_text(prompt: str) -> str:
    """
    基于语音识别的文本调用 DashScope Application 模型生成导航语义文本，并逐字打印输出。
    """
    global map_text

    if not prompt:
        print("❗ 未提供有效的 prompt，跳过地图分析")
        return ""

    try:
        responses = Application.call(
            api_key='sk-9073d9adbcf346debc161e2c2735c422',
            app_id='e9e84b1a672c433990a31c5e6edb6a77',
            prompt=prompt,
            stream=True,
            incremental_output=True
        )
    except Exception as e:
        print("DashScope 调用异常：", e)
        return ""

    map_text = ""
    print("🧭 地图分析结果：", end='', flush=True)
    for response in responses:
        if response.status_code != HTTPStatus.OK:
            print(f'\n⚠️ DashScope 调用失败 | request_id={response.request_id}')
            print(f'状态码: {response.status_code}, 消息: {response.message}')
            continue

        # 逐字符输出
        for char in response.output.text:
            print(char, end='', flush=True)
            time.sleep(0.1)
            map_text += char

    print()  # 输出完成换行
    return map_text
