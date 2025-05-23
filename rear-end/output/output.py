import asyncio
import websockets

async def upload_audio(file_path, filename):
    uri = "ws://127.0.0.1:8000/ws-audio"
    async with websockets.connect(uri) as websocket:
        # 先发送音频内容
        with open(file_path, "rb") as f:
            data = f.read()
        await websocket.send(data)
        # 再发送文件名
        await websocket.send(filename)
        # 接收服务器返回消息
        resp = await websocket.recv()
        print(resp)

if __name__ == "__main__":
    # 上传TTS生成的音频文件
    asyncio.run(upload_audio("../audio_text_audio/map.wav", "map.wav"))
    asyncio.run(upload_audio("../audio_text_audio/vl_max.wav", "vl_max.wav"))