# map/map.py
from http import HTTPStatus
from dashscope import Application

map_text = ""  # 全局缓存结果

def generate_map_text(prompt: str) -> str:
    """
    基于语音识别的文本调用 DashScope Application 模型生成导航语义文本
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
    for response in responses:
        if response.status_code != HTTPStatus.OK:
            print(f'⚠️ DashScope 调用失败 | request_id={response.request_id}')
            print(f'状态码: {response.status_code}, 消息: {response.message}')
            continue
        map_text += response.output.text

    print("🧭 地图分析结果：", map_text)
    return map_text
