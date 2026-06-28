"""
name_service.py
─────────────────────────────────────────────────────────────
خدمة اسم بسيطة (Simple Name Service / DNS-like layer).

الهدف: عدم الاعتماد على عنوان IP ومنفذ (Port) ظاهرين بشكل مباشر
داخل كود الكلاينت أو السيرفر. بدلاً من ذلك، يُستخدم اسم خدمة منطقي
(مثل "chat-server") يتم ترجمته (resolve) إلى (host, port) الحقيقيين
من خلال ملف تهيئة خارجي service_config.json.

هذا يحاكي بشكل مبسّط مبدأ عمل DNS: المستخدم/المطوّر يتعامل مع
اسم، وخدمة الاسم هي المسؤولة عن إيجاد العنوان الحقيقي المرتبط به.
"""

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "service_config.json")

DEFAULT_CONFIG = {
    "chat-server": {
        "host": "127.0.0.1",
        "port": 5000
    }
}


def _load_config():
    """تحميل ملف التهيئة، أو إنشاؤه بقيم افتراضية إذا لم يكن موجوداً."""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return dict(DEFAULT_CONFIG)


def resolve(service_name):
    """
    ترجمة اسم خدمة منطقي إلى (host, port) حقيقيين.

    مثال:
        host, port = resolve("chat-server")

    إذا لم يكن الاسم موجوداً بالتهيئة، يتم رفع استثناء واضح
    بدل فشل صامت.
    """
    config = _load_config()
    entry = config.get(service_name)

    if entry is None:
        raise ValueError(
            f"[NAME SERVICE] الخدمة '{service_name}' غير مسجّلة في {CONFIG_FILE}"
        )

    return entry["host"], entry["port"]


def register(service_name, host, port):
    """تسجيل أو تحديث خدمة جديدة بملف التهيئة (اختياري، للتوسعة المستقبلية)."""
    config = _load_config()
    config[service_name] = {"host": host, "port": port}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
