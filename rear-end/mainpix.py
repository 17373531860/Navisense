# mainpix.py

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
import io
import os
import threading
import requests
import subprocess  # 用于调用 VL_MAX.py
from typing import Optional

# 导入缓存模块（假设你有一个 api.py 文件）
from api import image_cache, audio_cache

app = FastAPI()

# 图片存储目录
IMAGE_STORAGE_DIR = "./image_cache"
os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)

# 音频缓存目录
os.makedirs("./audio_cache", exist_ok=True)
@app.on_event("startup")
async def startup_event():
    print("服务已启动，准备处理图片和音频上传与分析")


@app.get("/upload-media")
def upload_media_form():
    return HTMLResponse("""
        <h2>上传图片</h2>
        <form action="/upload-media" enctype="multipart/form-data" method="post">
            <input name="file" type="file" accept="image/*">
            <input type="submit" value="上传">
        </form>
    """)


@app.post("/upload-media")
async def upload_media(file: UploadFile = File(...)):
    content_type = file.content_type

    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片文件")

    # 读取原始数据
    data = await file.read()

    # 缓存到内存
    image_cache[file.filename] = data

    # 保存到本地磁盘
    file_path = os.path.join(IMAGE_STORAGE_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(data)

    print(f"图片已保存到: {file_path}")

    # 调用 VL_MAX.py 进行分析，并传递图片路径
    trigger_vl_analysis(file_path)

    return {
        "msg": "图片已上传并保存",
        "filename": file.filename,
        "file_path": file_path,
        "export_url": f"/get-media/{file.filename}"
    }


def trigger_vl_analysis(image_path):
    try:
        print(f"调用 VL_MAX.py 分析图片: {image_path}")
        process = subprocess.Popen(
            ["python", "-u", "video_and_image/VL_MAX.py", image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0
        )

        while True:
            char = process.stdout.read(1)
            if not char:
                break
            print(char.decode("gbk", errors="ignore"), end='', flush=True)

        process.stdout.close()
        process.wait()

        audio_file_path = "./audio_cache/vl_max.wav"
        if os.path.exists(audio_file_path):
            with open(audio_file_path, "rb") as f:
                audio_cache["vl_max.wav"] = f.read()
            print("音频文件已加入缓存：vl_max.wav")
        else:
            print("音频文件未找到，无法加入缓存")

        # === 新增：逐字打印 vl_max_output.txt 内容 ===
        output_file = "vl_max_output.txt"
        if os.path.exists(output_file):
            print("\n【图片分析文本结果】")
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                import time
                for char in content:
                    print(char, end='', flush=True)
                    time.sleep(0.1)  # 控制打字速度，可调整
                print()  # 打印结束后换行
        else:
            print("未找到 vl_max_output.txt，无法打印图片分析文本结果。")

    except Exception as e:
        print(f"调用 VL_MAX.py 时发生错误：{e}")


@app.get("/get-media/{filename}")
def get_media(filename: str):
    if filename in image_cache:
        data = image_cache[filename]
        return StreamingResponse(
            io.BytesIO(data),
            media_type="image/png",
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    else:
        raise HTTPException(status_code=404, detail="文件未找到")


@app.websocket("/ws-audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 接收音频数据和文件名
            data = await websocket.receive_bytes()
            print("收到音频数据长度：", len(data))

            filename = await websocket.receive_text()
            print("收到文件名：", filename)

            # 缓存到内存
            audio_cache[filename] = data

            # 保存到本地
            save_path = f"./audio_cache/{filename}"
            with open(save_path, "wb") as f:
                f.write(data)
            print(f"音频已保存至：{save_path}")

            await websocket.send_text(f"音频 {filename} 已缓存并保存")

            # 只做语音理解和地图分析
            try:
                from audio_text_audio.SST_fix import stt_process
                from map.map import generate_map_text

                stt_text = stt_process(filename)
                print("STT文本：", stt_text)

                if stt_text.strip():
                    map_result = generate_map_text(stt_text)
                    print("地图分析结果：", map_result)
                    await websocket.send_text(f"地图分析结果：{map_result}")
                else:
                    print("STT 文本为空，跳过地图生成")
                    await websocket.send_text("未识别到有效语音内容，未生成地图分析结果。")

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"处理音频时发生异常：{e}")
                await websocket.send_text(f"处理音频时发生异常：{e}")

    except WebSocketDisconnect:
        print("WebSocket 断开")


@app.get("/get-audio/{filename}")
def get_audio(filename: str):
    data = audio_cache.get(filename)
    if not data:
        raise HTTPException(status_code=404, detail="音频未找到")
    return StreamingResponse(
        io.BytesIO(data),
        media_type="audio/wav",
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.get("/get-audio-file/{filename}")
def get_audio_file(filename: str):
    """
    返回生成的音频文件
    """
    audio_file_path = os.path.join("./audio_cache", filename)
    if not os.path.exists(audio_file_path):
        raise HTTPException(status_code=404, detail="音频文件未找到")
    
    return StreamingResponse(
        open(audio_file_path, "rb"),
        media_type="audio/wav",
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.get("/")
def root():
    return {"msg": "服务已启动，支持图片上传与下载，音频通过WebSocket上传。访问 /docs 查看接口文档。"}