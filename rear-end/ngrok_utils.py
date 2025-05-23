# ngrok_utils.py

import requests

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
                return public_url.strip()  # 去除可能的空格或换行符

        print("❌ 未找到映射到 localhost:8000 的隧道")
        return None

    except requests.exceptions.ConnectionError:
        print("❌ ngrok Web Interface 未运行，请先启动 ngrok")
        return None
    except Exception as e:
        print(f"⚠️ 获取 ngrok 地址失败：{e}")
        return None