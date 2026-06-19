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
    │  $4,341.14  +0.75% ▲              IDR 2.471.332/gr      │  ← row 1 (tetap)
    │                                                          │
    │         ┌──────────────────────────────┐                 │
    │         │     IDR +18.490              │  ← kotak tengah │
    │         └──────────────────────────────┘                 │
    │                                                          │
    │  ┌───────────────────┐  ┌───────────────────────────┐   │
    │  │  Rp 2.718.816/gr  │  │  Buyback: Rp 2.286.277/gr │   │  ← 2 kotak bawah
    │  └───────────────────┘  └───────────────────────────┘   │
    │                                                          │
    │  KURS: Rp 17.707  |  16 Jun 2026 16:00 WIB  @brankasemas│  ← row bawah (tetap)
    └─────────────────────────────────────────────────────────┘

    """

    
    # ── Buat canvas ───────────────────────────────────────────
    if os.path.exists(TEMPLATE_PATH):
        img = Image.open(TEMPLATE_PATH).convert("RGB")
        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)
    else:
        img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), color=COLOR_BG)

    draw = ImageDraw.Draw(img)

    # ── Load fonts ────────────────────────────────────────────
    font_xl = load_font(FONT_PATH_BOLD,    130)
    font_lg = load_font(FONT_PATH_BOLD,     70)
    font_md = load_font(FONT_PATH_BOLD,     34)
    font_md1 = load_font(FONT_PATH_BOLD,    38)
    font_sm = load_font(FONT_PATH_REGULAR,  26)
    font_xs = load_font(FONT_PATH_REGULAR,  22)
    font_xs1 = load_font(FONT_PATH_REGULAR, 30)

    
    # ── Data ──────────────────────────────────────────────────
    xauusd_oz     = data.get("xauusd_oz", 0)
    idr_per_gram  = data.get("idr_per_gram", 0)
    antam_jual    = data.get("antam_jual", 0)
    antam_buyback = data.get("antam_buyback", 0)
    change_pct    = data.get("change_pct", 0)
    change_idr    = data.get("change_idr", 0)
    usd_idr       = data.get("usd_idr", 0)
    timestamp     = data.get("timestamp", "")

    is_up        = change_pct >= 0
    color_change = COLOR_GREEN if is_up else COLOR_RED
    arrow        = "▲" if is_up else "▼"

    
    # ── Ukuran canvas ─────────────────────────────────────
    W = IMAGE_WIDTH   # 1080
    H = IMAGE_HEIGHT  # 400

    # ────────────────────────────────────────────────────────
    # ROW 1: Harga USD | Persen | IDR per gram (atas)
    # ────────────────────────────────────────────────────────
    y1 = 20

    usd_text = fmt_usd(xauusd_oz)
    draw.text((24, y1), usd_text, font=font_md, fill=COLOR_WHITE)

    pct_text = f"  {fmt_pct(change_pct)} {arrow}"
    usd_w = draw.textlength(usd_text, font=font_md)
    draw.text((24 + usd_w, y1 + 4), pct_text, font=font_sm, fill=color_change)

    idr_gram_text = fmt_idr(idr_per_gram) + "/gr"
    idr_gram_w    = draw.textlength(idr_gram_text, font=font_md)
    draw.text((W - idr_gram_w - 24, y1), idr_gram_text, font=font_md, fill=COLOR_WHITE)

    # ────────────────────────────────────────────────────────
    # KOTAK TENGAH: Estimasi Kenaikan/Penurunan
    # Posisi: tengah horizontal, 1/3 dari atas
    # ────────────────────────────────────────────────────────
    box1_x1, box1_y1 = 220, 90
    box1_x2, box1_y2 = 860, 230

    # Label kecil di atas kotak
    label1 = "Estimasi Kenaikan Harga" if change_idr >= 0 else "Estimasi Penurunan Harga"
    label1_w = draw.textlength(label1, font=font_xs1)
    draw.text(((box1_x1 + box1_x2) // 2 - label1_w // 2, box1_y1 + 10),
              label1, font=font_xs1, fill=COLOR_WHITE)

    # Angka besar di tengah kotak
    sign_idr = "+" if change_idr >= 0 else "-"
    big_text = f"{arrow} IDR {sign_idr}{abs(change_idr):,.0f}".replace(",", ".")
    big_w    = draw.textlength(big_text, font=font_lg)
    big_x    = (box1_x1 + box1_x2) // 2 - big_w // 2
    big_y    = box1_y1 + 42
    draw.text((big_x + 2, big_y + 2), big_text, font=font_lg, fill=(0, 0, 0))
    draw.text((big_x, big_y), big_text, font=font_lg, fill=color_change)

    # ────────────────────────────────────────────────────────
    # KOTAK KIRI BAWAH: Estimasi Harga Jual Antam
    # ────────────────────────────────────────────────────────
    box2_x1, box2_y1 = 24,  250
    box2_x2, box2_y2 = 516, 360

    # Label
    label2   = "Estimasi Harga Jual Antam"
    label2_w = draw.textlength(label2, font=font_xs)
    draw.text(((box2_x1 + box2_x2) // 2 - label2_w // 2, box2_y1 + 10),
              label2, font=font_xs, fill=COLOR_WHITE)

    # Nilai
    jual_text = fmt_rp(antam_jual) + "/gr"
    jual_w    = draw.textlength(jual_text, font=font_md1)
    draw.text(((box2_x1 + box2_x2) // 2 - jual_w // 2, box2_y1 + 42),
              jual_text, font=font_md1, fill=COLOR_YELLOW)

    # ────────────────────────────────────────────────────────
    # KOTAK KANAN BAWAH: Estimasi Harga Buyback Antam
    # ────────────────────────────────────────────────────────
    box3_x1, box3_y1 = 540, 250
    box3_x2, box3_y2 = 1056, 360

    # Label
    label3   = "Estimasi Harga Buyback Antam"
    label3_w = draw.textlength(label3, font=font_xs)
    draw.text(((box3_x1 + box3_x2) // 2 - label3_w // 2, box3_y1 + 10),
              label3, font=font_xs, fill=COLOR_WHITE)

    # Nilai
    bb_text = fmt_rp(antam_buyback) + "/gr"
    bb_w    = draw.textlength(bb_text, font=font_md1)
    draw.text(((box3_x1 + box3_x2) // 2 - bb_w // 2, box3_y1 + 42),
              bb_text, font=font_md1, fill=COLOR_ACCENT)

    # ────────────────────────────────────────────────────────
    # ROW BAWAH: Kurs + Timestamp + Watermark
    # ────────────────────────────────────────────────────────
    y4 = H - 36

    kurs_text = f"KURS: {fmt_rp(usd_idr)}  |  {timestamp}"
    draw.text((24, y4), kurs_text, font=font_xs, fill=COLOR_GRAY)

    wm_text = "@brankasemas.idn"
    wm_w    = draw.textlength(wm_text, font=font_xs)
    draw.text((W - wm_w - 24, y4), wm_text, font=font_xs, fill=COLOR_WHITE)

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
