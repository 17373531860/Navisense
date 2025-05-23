import requests
import asyncio
import websockets
import os

def upload_video(file_path, filename):
    url = "http://127.0.0.1:8000/upload-media"
    with open(file_path, "rb") as f:
        files = {"file": (filename, f, "video/mp4")}
        response = requests.post(url, files=files)
    print("视频上传结果：", response.json())

async def upload_audio(file_path, filename):
    uri = "ws://127.0.0.1:8000/ws-audio"
    async with websockets.connect(uri) as websocket:
        with open(file_path, "rb") as f:
            data = f.read()
        print("准备上传音频，长度：", len(data))
        await websocket.send(data)
        await websocket.send(filename)
        resp = await websocket.recv()
        print("音频上传结果：", resp)

if __name__ == "__main__":
    # 测试上传视频
    if os.path.exists("test_video.mp4"):
        upload_video("test_video.mp4", "test_video.mp4")
    else:
        print("test_video.mp4 文件不存在")
    # 测试上传音频
    if os.path.exists("test_audio.wav"):
        asyncio.run(upload_audio("test_audio.wav", "test_audio.wav"))
    else:
        print("test_audio.wav 文件不存在")