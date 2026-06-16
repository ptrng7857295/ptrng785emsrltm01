import requests
import json
from datetime import datetime, timezone, timedelta
WIB = timezone(timedelta(hours=7))
from config import (
    GOLD_API_KEY, GOLD_API_URL,
    EXCHANGE_API_URL,
    ANTAM_JUAL_MARKUP, ANTAM_BUYBACK_MARKUP
)

def fetch_xauusd() -> float:
    """Ambil harga XAUUSD dalam troy ounce dari Goldapi.io"""
    headers = {
        "x-access-token": GOLD_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        res = requests.get(GOLD_API_URL, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        price = data.get("price", 0)
        print(f"[fetch] XAUUSD: ${price:,.2f}")
        return float(price)
    except Exception as e:
        print(f"[fetch] ERROR ambil XAUUSD: {e}")
        return 0.0


def fetch_usd_idr() -> float:
    """Ambil kurs USD/IDR dari ExchangeRate API"""
    try:
        res = requests.get(EXCHANGE_API_URL, timeout=10)
        res.raise_for_status()
        data = res.json()
        rate = data.get("conversion_rate", 0)
        print(f"[fetch] USD/IDR: Rp {rate:,.0f}")
        return float(rate)
    except Exception as e:
        print(f"[fetch] ERROR ambil kurs: {e}")
        return 0.0


def get_price_data() -> dict:
    """
    Hitung semua data harga yang diperlukan untuk generate gambar.
    
    Returns dict berisi:
    - xauusd_oz      : harga XAU per troy ounce (USD)
    - xauusd_gram    : harga XAU per gram (USD)
    - usd_idr        : kurs USD ke IDR
    - idr_per_gram   : harga emas per gram (IDR)
    - antam_jual     : proyeksi harga jual Antam per gram (IDR)
    - antam_buyback  : proyeksi harga buyback Antam per gram (IDR)
    - change_pct     : perubahan harga (%) — dari API jika tersedia
    - change_idr     : selisih harga IDR per gram vs kemarin
    - timestamp      : waktu fetch (WIB)
    """

    xauusd_oz  = fetch_xauusd()
    usd_idr    = fetch_usd_idr()

    # 1 troy ounce = 31.1035 gram
    TROY_OZ_TO_GRAM = 31.1035

    xauusd_gram  = xauusd_oz / TROY_OZ_TO_GRAM
    idr_per_gram = xauusd_gram * usd_idr

    antam_jual    = idr_per_gram * ANTAM_JUAL_MARKUP
    antam_buyback = idr_per_gram * ANTAM_BUYBACK_MARKUP

    # Simulasi change (idealnya ambil dari API previous close)
    # Goldapi.io menyediakan field prev_close_price
    try:
        headers = {"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
        res = requests.get(GOLD_API_URL, headers=headers, timeout=10)
        raw = res.json()
        prev_close = raw.get("prev_close_price", xauusd_oz)
        change_oz  = xauusd_oz - prev_close
        change_pct = (change_oz / prev_close * 100) if prev_close else 0
        change_idr = (change_oz / TROY_OZ_TO_GRAM) * usd_idr
    except Exception:
        change_pct = 0.0
        change_idr = 0.0

    data = {
        "xauusd_oz"     : xauusd_oz,
        "xauusd_gram"   : xauusd_gram,
        "usd_idr"       : usd_idr,
        "idr_per_gram"  : idr_per_gram,
        "antam_jual"    : antam_jual,
        "antam_buyback" : antam_buyback,
        "change_pct"    : change_pct,
        "change_idr"    : change_idr,
        "timestamp" : datetime.now(WIB).strftime("%d %b %Y %H:%M WIB")
    }

    print(f"\n[fetch] ── RINGKASAN ──────────────────────")
    print(f"  XAUUSD/oz   : ${xauusd_oz:,.2f}")
    print(f"  XAUUSD/gram : ${xauusd_gram:,.4f}")
    print(f"  USD/IDR     : Rp {usd_idr:,.0f}")
    print(f"  IDR/gram    : Rp {idr_per_gram:,.0f}")
    print(f"  Antam Jual  : Rp {antam_jual:,.0f}")
    print(f"  Antam BB    : Rp {antam_buyback:,.0f}")
    print(f"  Change      : {change_pct:+.2f}% | IDR {change_idr:+,.0f}/gr")
    print(f"  Waktu       : {data['timestamp']}")
    print(f"────────────────────────────────────────\n")

    return data


if __name__ == "__main__":
    result = get_price_data()
    print(json.dumps(result, indent=2, default=str))
