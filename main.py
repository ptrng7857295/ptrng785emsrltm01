"""
main.py — Jalankan pipeline lengkap sekali:
  1. Fetch harga XAUUSD + kurs IDR
  2. Generate gambar overlay
  3. Post ke Threads

Usage:
  python main.py           → jalankan 1x
  python main.py --dry-run → fetch + generate gambar, skip post
"""

import sys
import traceback
from datetime import datetime

import importlib

fetch_mod    = importlib.import_module("1_fetch_price")
generate_mod = importlib.import_module("2_generate_image")
post_mod     = importlib.import_module("3_post_threads")

get_price_data  = fetch_mod.get_price_data
generate_image  = generate_mod.generate_image
post_to_threads = post_mod.post_to_threads


def run(dry_run: bool = False):
    import time
    import random
    sleep_sec = random.randint(120, 240)  # random antara 2-4 menit
    print(f"[main] Menunggu {sleep_sec} detik sebelum fetch...")
    time.sleep(sleep_sec)
  
    print(f"\n{'='*50}")
    print(f"  EMASREALTIME — {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print(f"{'='*50}")

    # ── STEP 1: Fetch harga ──────────────────────────────────
    print("\n[1/3] Fetching harga...")
    try:
        data = get_price_data()
    except Exception as e:
        print(f"[main] ❌ Gagal fetch harga: {e}")
        traceback.print_exc()
        return False

    if not data or data.get("xauusd_oz", 0) == 0:
        print("[main] ❌ Data harga kosong, skip cycle ini.")
        return False

    # ── STEP 2: Generate gambar ──────────────────────────────
    print("\n[2/3] Generate gambar...")
    try:
        image_path = generate_image(data)
    except Exception as e:
        print(f"[main] ❌ Gagal generate gambar: {e}")
        traceback.print_exc()
        return False

    # ── STEP 3: Post ke Threads ──────────────────────────────
    if dry_run:
        print("\n[3/3] DRY RUN — skip posting ke Threads.")
        print(f"[main] ✅ Gambar tersedia di: {image_path}")
        return True

    print("\n[3/3] Posting ke Threads...")
    try:
        success = post_to_threads(data, image_path)
        if success:
            print("[main] ✅ Selesai! Post berhasil dikirim.")
        else:
            print("[main] ⚠️  Post gagal, cek log di atas.")
        return success
    except Exception as e:
        print(f"[main] ❌ Error saat posting: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run(dry_run=dry)
