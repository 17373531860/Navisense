# mainpix.py

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
import io
import os
import threading
import requests
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
    print("服务已启动，准备处理图片上传与分析")


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

    # 触发异步图像分析
    trigger_vl_analysis(image=file.filename)

    return {
        "msg": "图片已上传并保存",
        "filename": file.filename,
        "export_url": f"/get-media/{file.filename}"
    }


# ========== 新增：ngrok 获取公网地址 + 异步分析函数 ==========

def get_ngrok_public_url():
    """
    从本地 ngrok Web Interface 获取映射到 localhost:8000 的公网地址
    """
    NGROK_API_URL = "http://localhost:4040/api/tunnels"

    try:
        response = requests.get(NGROK_API_URL)
        response.raise_for_status()
        data = response.json()

        for tunnel in data.get("tunnels", []):
            if tunnel.get("config", {}).get("addr") == "http://localhost:8000":
                public_url = tunnel.get("public_url")
                print(f"✅ 成功获取 ngrok 地址：{public_url}")
                return public_url.strip()  # 去除空格和换行符

        print("❌ 未找到映射到 localhost:8000 的隧道")
        return None

    except requests.exceptions.ConnectionError:
        print("❌ ngrok Web Interface 未运行，请先启动 ngrok")
        return None
    except Exception as e:
        print(f"⚠️ 获取 ngrok 地址失败：{e}")
        return None


def async_analyze(image_filename: str):
    """
    异步执行图像分析任务（不阻塞主线程）
    """
    public_url = get_ngrok_public_url()
    if not public_url:
        print("❌ 无法获取 ngrok 地址，跳过分析")
        return

    image_url = f"{public_url}/get-media/{image_filename}"
    print(f"🌐 正在使用公网 URL 分析图片：{image_url}")

    from vl_analyzer import analyze_image_with_qwen_vl_max
    result = analyze_image_with_qwen_vl_max(image_url)
    print(f"🔍 图像分析结果（{image_filename}）：{result}")


def trigger_vl_analysis(image: str = None):
    if image:
        thread = threading.Thread(target=async_analyze, args=(image,))
        thread.start()
    else:
        raise ValueError("必须提供 image 参数")


# ========== 基础接口 ==========

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

            # 调用 STT 与地图分析（可选）
            try:
                from audio_text_audio.SST import stt_process
                from map.map import generate_map_text

                stt_text = stt_process(filename)
                print("STT文本：", stt_text)

                if stt_text.strip():
                    map_result = generate_map_text(stt_text)
                    print("地图分析结果：", map_result)
                else:
                    print("STT 文本为空，跳过地图生成")

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"处理音频时发生异常：{e}")

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


@app.get("/")
def root():
    return {"msg": "服务已启动，支持图片上传与下载，音频通过WebSocket上传。访问 /docs 查看接口文档。"}