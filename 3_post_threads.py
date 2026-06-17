import requests
import time
import os
from config import THREADS_USER_ID, THREADS_ACCESS_TOKEN, OUTPUT_PATH

BASE_URL = "https://graph.threads.net/v1.0"

import random

HASHTAG_LIST = [
    "#Antamlogammulia",
    "#investasiemas",
    "#beliemas",
    "#brankasemas",
    "#HargaEmasHariIni",
    "#juallogammulia",
    "#logammuliaantam",
    "#emasantam",
    "#GoldThreads",
    "#pegadaian",
    "#tangsel",
    "#Nyabarantam",
    "#LogamMulia",
    "#jewelrythreads",
    "#investing",
    "#jakarta",
]


PROMOSI_LIST = [
    "Mau update harga emas tiap saat? Yuk gabung grup kami, link ada di bio 👆",
    "Info lebih lengkap ada di grup kami, cek link di bio 📲",
    "Dapatkan notifikasi harga emas di WA, link bergabung ada di bio",
    "Diskusi & update harga emas setiap saat, gabung sekarang link di bio",
    "Komunitas investor emas aktif, join sekarang! Link ada di bio 👆",
    "Jangan ketinggalan update harga, join grup kami lewat link di bio 📊",
    "Ratusan investor emas sudah gabung, giliranmu! Link di bio 🔗",
    "Grup khusus pantau harga emas, join via link yang ada di bio ya",
    "Update harga emas realtime langsung di grup kami, link bergabung di bio 💰",
]



def fmt_idr_caption(value: float, prefix: str = "Rp ") -> str:
    """Format angka IDR untuk caption: titik sebagai pemisah ribuan"""
    return f"{prefix}{abs(value):,.0f}".replace(",", ".")


def build_caption(data: dict) -> str:
    """Buat caption teks untuk post Threads"""

    change_pct   = data.get("change_pct", 0)
    change_idr   = data.get("change_idr", 0)
    idr_per_gram = data.get("idr_per_gram", 0)
    antam_jual   = data.get("antam_jual", 0)
    antam_buyback= data.get("antam_buyback", 0)
    usd_idr      = data.get("usd_idr", 0)
    timestamp    = data.get("timestamp", "")

    arah      = "📈 NAIK" if change_pct >= 0 else "📉 TURUN"
    sign_idr  = "+" if change_idr >= 0 else "-"
    sign_pct  = "+" if change_pct >= 0 else ""

    caption = (
        f"⚡ UPDATE HARGA EMAS ⚡ (Algo 2) \n\n {timestamp}\n\n"
        f"{arah} {sign_pct}{change_pct:.2f}%\n"
        f"Perubahan: IDR {sign_idr}{fmt_idr_caption(change_idr, prefix='')}/gr\n\n"
        f"💰 Harga Emas Dunia : {fmt_idr_caption(idr_per_gram)}/gr\n"
        f"🛒 Estimasi Antam : {fmt_idr_caption(antam_jual)}/gr\n"
        f"💵 Antam Buyback: {fmt_idr_caption(antam_buyback)}/gr\n\n"
        f"💱 Kurs USD/IDR   : {fmt_idr_caption(usd_idr)}\n\n"
        f"{random.choice(PROMOSI_LIST)}\n"
        f"{random.choice(HASHTAG_LIST)}\n"
    )

    return caption


def create_media_container(image_path: str, caption: str) -> str | None:
    """
    Step 1: Upload gambar ke Threads → dapat media container ID.
    Gambar harus bisa diakses via URL publik.
    
    CATATAN: Threads API memerlukan URL publik, bukan upload file langsung.
    Opsi: upload dulu ke imgbb.com / Cloudinary / server sendiri.
    Di sini kita pakai imgbb (gratis).
    """

    # ── Upload ke ImgBB dulu (gratis, dapat URL publik) ────
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")

    with open(image_path, "rb") as f:
        img_data = f.read()

    import base64
    encoded = base64.b64encode(img_data).decode("utf-8")

    imgbb_res = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            "key": IMGBB_API_KEY,
            "image": encoded,
            "expiration": 600  # hapus otomatis setelah 10 menit
        },
        timeout=30
    )

    if imgbb_res.status_code != 200:
        print(f"[post] ERROR upload ImgBB: {imgbb_res.text}")
        return None

    image_url = imgbb_res.json()["data"]["url"]
    print(f"[post] Gambar tersedia di: {image_url}")

    # ── Buat media container di Threads ────────────────────
    url = f"{BASE_URL}/{THREADS_USER_ID}/threads"
    params = {
        "media_type"    : "IMAGE",
        "image_url"     : image_url,
        "text"          : caption,
        "access_token"  : THREADS_ACCESS_TOKEN
    }

    res = requests.post(url, params=params, timeout=15)
    if res.status_code != 200:
        print(f"[post] ERROR buat container: {res.text}")
        return None

    container_id = res.json().get("id")
    print(f"[post] Container ID: {container_id}")
    return container_id


def publish_container(container_id: str) -> bool:
    """
    Step 2: Publish container yang sudah dibuat.
    Threads butuh jeda ~30 detik setelah create sebelum publish.
    """

    print("[post] Menunggu 30 detik sebelum publish...")
    time.sleep(30)

    url = f"{BASE_URL}/{THREADS_USER_ID}/threads_publish"
    params = {
        "creation_id"  : container_id,
        "access_token" : THREADS_ACCESS_TOKEN
    }

    res = requests.post(url, params=params, timeout=15)
    if res.status_code != 200:
        print(f"[post] ERROR publish: {res.text}")
        return False

    post_id = res.json().get("id")
    print(f"[post] ✅ Berhasil diposting! Post ID: {post_id}")
    return True


def post_to_threads(data: dict, image_path: str = OUTPUT_PATH) -> bool:
    """Fungsi utama: build caption → upload gambar → post ke Threads"""

    if not THREADS_USER_ID or not THREADS_ACCESS_TOKEN:
        print("[post] ⚠️  THREADS_USER_ID atau THREADS_ACCESS_TOKEN belum diset di .env")
        return False

    caption      = build_caption(data)
    container_id = create_media_container(image_path, caption)

    if not container_id:
        return False

    return publish_container(container_id)


# ─── TEST LANGSUNG ──────────────────────────────────────────
if __name__ == "__main__":
    dummy = {
        "xauusd_oz"     : 4072.43,
        "idr_per_gram"  : 2375201,
        "antam_jual"    : 2619000,
        "antam_buyback" : 2393000,
        "change_pct"    : -3.64,
        "change_idr"    : -93693,
        "usd_idr"       : 18141,
        "timestamp"     : "11 Jun 2026 04:00 WIB"
    }
    post_to_threads(dummy)
