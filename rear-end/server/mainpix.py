from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
import io

app = FastAPI()

image_cache = {}
video_cache = {}
audio_cache = {}

@app.get("/upload-media")
def upload_media_form():
    return HTMLResponse("""
        <h2>上传图片或视频</h2>
        <form action="/upload-media" enctype="multipart/form-data" method="post">
            <input name="file" type="file" accept="image/*,video/*">
            <input type="submit" value="上传">
        </form>
    """)

@app.post("/upload-media")
async def upload_media(file: UploadFile = File(...)):
    data = await file.read()
    content_type = file.content_type
    if content_type.startswith("image/"):
        image_cache[file.filename] = data
        return {
            "msg": "图片已缓存",
            "filename": file.filename,
            "export_url": f"/get-media/{file.filename}"
        }
    elif content_type.startswith("video/"):
        video_cache[file.filename] = data
        return {
            "msg": "视频已缓存",
            "filename": file.filename,
            "export_url": f"/get-media/{file.filename}"
        }
    else:
        raise HTTPException(status_code=400, detail="仅支持图片或视频文件")

@app.get("/get-media/{filename}")
def get_media(filename: str):
    if filename in image_cache:
        data = image_cache[filename]
        return StreamingResponse(
            io.BytesIO(data),
            media_type="image/png",  # 可根据实际类型调整
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    elif filename in video_cache:
        data = video_cache[filename]
        return StreamingResponse(
            io.BytesIO(data),
            media_type="video/mp4",
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
    else:
        raise HTTPException(status_code=404, detail="文件未找到")

@app.websocket("/ws-audio")
async def websocket_audio(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            # 这里假设客户端先发送文件名，再发送音频内容
            # 你可以根据实际需求调整协议
            # 例如：先发送文本类型的文件名，再发送二进制音频数据
            # 这里只做简单演示，假设每次只上传一个音频文件
            filename = await websocket.receive_text()
            audio_cache[filename] = data
            await websocket.send_text(f"音频 {filename} 已缓存")
    except WebSocketDisconnect:
        pass

@app.get("/get-audio/{filename}")
def get_audio(filename: str):
    data = audio_cache.get(filename)
    if not data:
        raise HTTPException(status_code=404, detail="音频未找到")
    return StreamingResponse(
        io.BytesIO(data),
        media_type="audio/wav",  # 可根据实际类型调整
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

@app.get("/")
def root():
    return {"msg": "服务已启动，支持图片、视频上传与下载，音频通过WebSocket Secure上传。访问 /docs 查看接口文档。"}