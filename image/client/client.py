import os
import sys
import grpc
import requests
import urllib.parse
from typing import List, Tuple

# 讓 Python 找到 image_pb2
sys.path.append(os.path.dirname(__file__))

import image_pb2
import image_pb2_grpc

# 根目錄 output/
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "output"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_image_from_url(url: str) -> bytes:
    print(f"🌐 從 URL 下載圖片：{url}")
    decoded_url = urllib.parse.unquote(url)
    safe_url = urllib.parse.quote(decoded_url, safe=":/?&=%")

    try:
        response = requests.get(safe_url)
        if response.status_code == 200:
            return response.content
        raise Exception(f"❌ 下載失敗，狀態碼：{response.status_code}")
    except Exception as e:
        raise Exception(f"❌ 請求 URL 錯誤：{safe_url}\n訊息：{e}")

def generate_image(prompt: str) -> Tuple[str, str]:
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = image_pb2_grpc.ImageServiceStub(channel)
        request = image_pb2.ImageRequest(prompt=prompt)
        response = stub.GenerateImage(request)

        ext = response.file_type or "png"
        filename = f"{response.prompt_hash}.{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            print(f"📦 快取命中：{filepath}")
        else:
            if response.image_data:
                image_data = response.image_data
            elif response.image_url:
                image_data = download_image_from_url(response.image_url)
            else:
                raise Exception("❌ 沒有圖片資料")

            with open(filepath, "wb") as f:
                f.write(image_data)
            print(f"✅ 圖片已儲存：{filepath}")

        return filepath, response.prompt_hash

def generate_batch(prompts: List[str]) -> List[Tuple[str, str, str]]:
    """批次產圖並儲存至 output 資料夾"""
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = image_pb2_grpc.ImageServiceStub(channel)
        request = image_pb2.BatchRequest(prompts=prompts)
        response = stub.GenerateBatch(request)

    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
    os.makedirs(output_dir, exist_ok=True)

    results = []

    for item in response.items:
        filename = f"{item.prompt_hash}.{item.file_type or 'png'}"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            print(f"📦 快取命中：{filepath}")
        else:
            with open(filepath, "wb") as f:
                f.write(item.image_data)
            print(f"✅ 圖片已儲存：{filepath}")

        results.append((item.prompt_hash, item.prompt, filepath))

    return results