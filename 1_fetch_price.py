import requests
import json
import yfinance as yf
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

from config import (
    EXCHANGE_API_URL,
    ANTAM_JUAL_MARKUP, ANTAM_BUYBACK_MARKUP
)

TROY_OZ_TO_GRAM    = 31.1035
FUTURES_SPOT_DIFF  = 17.0  # Koreksi selisih Futures vs Spot


def fetch_xauusd() -> tuple[float, float]:
    """
    Ambil harga XAUUSD realtime dari Yahoo Finance (GC=F = Gold Futures).
    Dikurangi FUTURES_SPOT_DIFF untuk mendekati harga spot TradingView.
    Returns: (harga_sekarang, prev_close)
    """
    try:
        ticker     = yf.Ticker("GC=F")
        info       = ticker.fast_info
        price      = float(info["last_price"])      - FUTURES_SPOT_DIFF
        prev_close = float(info["previous_close"])  - FUTURES_SPOT_DIFF
        print(f"[fetch] XAUUSD: ${price:,.2f} | Prev Close: ${prev_close:,.2f}")
        return price, prev_close
    except Exception as e:
        print(f"[fetch] ERROR ambil XAUUSD: {e}")
        # Fallback ke history jika fast_info gagal
        try:
            ticker     = yf.Ticker("GC=F")
            hist       = ticker.history(period="2d", interval="1d")
            price      = float(hist["Close"].iloc[-1])     - FUTURES_SPOT_DIFF
            prev_close = float(hist["Close"].iloc[-2])     - FUTURES_SPOT_DIFF
            print(f"[fetch] FALLBACK history XAUUSD: ${price:,.2f}")
            return price, prev_close
        except Exception as e2:
            print(f"[fetch] ERROR fallback history: {e2}")
            return 0.0, 0.0


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
    - antam_jual     : estimasi harga jual Antam per gram (IDR)
    - antam_buyback  : estimasi harga buyback Antam per gram (IDR)
    - change_pct     : perubahan harga (%) vs prev close
    - change_idr     : selisih harga IDR per gram vs kemarin
    - timestamp      : waktu fetch (WIB)
    """

    xauusd_oz, prev_close = fetch_xauusd()
    usd_idr               = fetch_usd_idr()

    xauusd_gram  = xauusd_oz / TROY_OZ_TO_GRAM if xauusd_oz else 0
    idr_per_gram = xauusd_gram * usd_idr

    antam_jual    = idr_per_gram * ANTAM_JUAL_MARKUP
    antam_buyback = idr_per_gram * ANTAM_BUYBACK_MARKUP

    # Hitung perubahan vs prev close
    if prev_close and prev_close > 0:
        change_oz  = xauusd_oz - prev_close
        change_pct = (change_oz / prev_close) * 100
        change_idr = (change_oz / TROY_OZ_TO_GRAM) * usd_idr
    else:
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
        "timestamp"     : datetime.now(WIB).strftime("%d %b %Y %H:%M WIB")
    }

    print(f"\n[fetch] ── RINGKASAN ──────────────────────")
    print(f"  XAUUSD/oz   : ${xauusd_oz:,.2f}")
    print(f"  Prev Close  : ${prev_close:,.2f}")
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
