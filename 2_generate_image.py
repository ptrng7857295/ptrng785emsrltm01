from PIL import Image, ImageDraw, ImageFont
import os
from config import (
    OUTPUT_PATH, IMAGE_WIDTH, IMAGE_HEIGHT,
    TEMPLATE_PATH,
    FONT_PATH_BOLD, FONT_PATH_REGULAR,
    COLOR_BG, COLOR_WHITE, COLOR_RED, COLOR_GREEN,
    COLOR_YELLOW, COLOR_GRAY, COLOR_ACCENT
)


# ─── HELPER: Load font dengan fallback ──────────────────────
def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        # Fallback ke default jika font tidak ditemukan
        print(f"[image] Font tidak ditemukan: {path}, pakai default")
        return ImageFont.load_default()


# ─── HELPER: Format angka IDR ───────────────────────────────
def fmt_idr(value: float, prefix: str = "IDR ") -> str:
    """Format angka ke format Rupiah: titik sebagai pemisah ribuan"""
    formatted = f"{abs(value):,.0f}".replace(",", ".")
    return f"{prefix}{formatted}"


def fmt_rp(value: float) -> str:
    """Format ke Rp dengan titik pemisah ribuan"""
    return fmt_idr(value, prefix="Rp ")


def fmt_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def fmt_usd(value: float) -> str:
    """Format USD: gunakan koma sebagai pemisah ribuan, titik desimal"""
    return f"${value:,.2f}"


# ─── MAIN FUNCTION ──────────────────────────────────────────
def generate_image(data: dict) -> str:
    """
    Generate gambar harga emas realtime mirip @emasrealtime.
    
    Layout:
    ┌─────────────────────────────────────────────────────────┐
    │  $4.072,43  -3.64% ▼   IDR 2.375.201/gr      [logo]   │
    │                                                          │
    │              IDR -93.693                                 │
    │                                                          │
    │   Proyeksi Antam → Rp 2.619.000/gr                      │
    │   Buyback → Rp 2.393.000/gr       [timestamp]           │
    └─────────────────────────────────────────────────────────┘
    """

    # ── Buat canvas ───────────────────────────────────────────
    if os.path.exists(TEMPLATE_PATH):
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
    else:
        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=COLOR_BG)
    
    draw = ImageDraw.Draw(img)

    # ── Load fonts ────────────────────────────────────────────
    font_xl     = load_font(FONT_PATH_BOLD,    130)  # angka besar IDR change
    font_lg     = load_font(FONT_PATH_BOLD,     46)  # harga IDR/gram
    font_md     = load_font(FONT_PATH_BOLD,     34)  # USD price
    font_sm     = load_font(FONT_PATH_REGULAR,  26)  # label kecil
    font_xs     = load_font(FONT_PATH_REGULAR,  22)  # timestamp, watermark

    W = IMAGE_WIDTH
    H = IMAGE_HEIGHT

    # ── Data ──────────────────────────────────────────────────
    xauusd_oz    = data.get("xauusd_oz", 0)
    idr_per_gram = data.get("idr_per_gram", 0)
    antam_jual   = data.get("antam_jual", 0)
    antam_buyback= data.get("antam_buyback", 0)
    change_pct   = data.get("change_pct", 0)
    change_idr   = data.get("change_idr", 0)
    usd_idr      = data.get("usd_idr", 0)
    timestamp    = data.get("timestamp", "")

    is_up = change_pct >= 0
    color_change = COLOR_GREEN if is_up else COLOR_RED
    arrow = "▲" if is_up else "▼"

    # ────────────────────────────────────────────────────────
    # ROW 1: Harga USD | Persen | IDR per gram
    # ────────────────────────────────────────────────────────
    y1 = 28

    # Harga USD (format internasional: $4,072.43)
    usd_text = fmt_usd(xauusd_oz)
    draw.text((24, y1), usd_text, font=font_md, fill=COLOR_WHITE)

    # Persentase + arrow
    pct_text = f"  {fmt_pct(change_pct)} {arrow}"
    usd_w = draw.textlength(usd_text, font=font_md)
    draw.text((24 + usd_w, y1 + 4), pct_text, font=font_sm, fill=color_change)

    # IDR per gram (kanan tengah) — format: IDR 2.375.201/gr
    idr_gram_text = fmt_idr(idr_per_gram) + "/gr"
    idr_gram_w    = draw.textlength(idr_gram_text, font=font_md)
    draw.text((W - idr_gram_w - 24, y1), idr_gram_text, font=font_md, fill=COLOR_WHITE)

    # ────────────────────────────────────────────────────────
    # ROW 2: ANGKA BESAR — Perubahan IDR (tengah)
    # ────────────────────────────────────────────────────────
    sign_idr = "+" if change_idr >= 0 else "-"
    big_text = f"IDR {sign_idr}{abs(change_idr):,.0f}".replace(",", ".")
    big_w    = draw.textlength(big_text, font=font_xl)
    big_x    = (W - big_w) // 2
    big_y    = H // 2 - 80

    # Shadow tipis supaya terbaca di atas chart
    draw.text((big_x + 3, big_y + 3), big_text, font=font_xl, fill=(0, 0, 0, 128))
    draw.text((big_x, big_y), big_text, font=font_xl, fill=color_change)

    # ────────────────────────────────────────────────────────
    # ROW 3: Proyeksi & Buyback Antam (bawah)
    # ────────────────────────────────────────────────────────
    y3 = H - 72

    # Separator line
    draw.line([(24, y3 - 14), (W - 24, y3 - 14)], fill=(50, 50, 60), width=1)

    # Proyeksi Antam — format: antam → Rp 2.619.000/gr
    proj_label = "Proyeksi "
    proj_val   = f"antam → {fmt_rp(antam_jual)}/gr"
    draw.text((24, y3), proj_label, font=font_sm, fill=COLOR_GRAY)
    proj_lw = draw.textlength(proj_label, font=font_sm)
    draw.text((24 + proj_lw, y3), proj_val, font=font_sm, fill=COLOR_YELLOW)



    # ────────────────────────────────────────────────────────
    # ROW 4: Kurs + Timestamp (paling bawah)
    # ────────────────────────────────────────────────────────
    y4 = H - 36

    kurs_text = f"KURS: {fmt_rp(usd_idr)}  |  {timestamp}"
    draw.text((24, y4), kurs_text, font=font_xs, fill=COLOR_GRAY)

    # Watermark akun
    wm_text = "www.brankasemas.com"
    wm_w    = draw.textlength(wm_text, font=font_xs)
    draw.text((W - wm_w - 24, y4), wm_text, font=font_xs, fill=(80, 80, 90))

    # ─── Simpan output ────────────────────────────────────────
    os.makedirs("output", exist_ok=True)
    img.save(OUTPUT_PATH, "PNG", quality=95)
    print(f"[image] Gambar disimpan: {OUTPUT_PATH}")
    return OUTPUT_PATH


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
    path = generate_image(dummy)
    print(f"[image] Output: {path}")
