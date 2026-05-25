"""结果缓存层：基于论文文件哈希，确保同一篇论文总是返回相同结果"""
import hashlib
import json
import os
import time


CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", ".cache")
CACHE_EXPIRY = 3600  # 1小时过期


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def file_hash(file_path: str) -> str:
    """计算文件的MD5哈希"""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def cache_key(file_path: str) -> str:
    """生成缓存键"""
    return file_hash(file_path)


def get_cached(file_path: str) -> dict | None:
    """获取缓存的结果"""
    key = cache_key(file_path)
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_path):
        mtime = os.path.getmtime(cache_path)
        if time.time() - mtime < CACHE_EXPIRY:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def save_cache(file_path: str, result: dict):
    """保存结果到缓存"""
    _ensure_cache_dir()
    key = cache_key(file_path)
    cache_path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
