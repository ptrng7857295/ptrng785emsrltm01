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

from fetch_price    import get_price_data
from generate_image import generate_image
from post_threads   import post_to_threads


def run(dry_run: bool = False):
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
