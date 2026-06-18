import os
from dotenv import load_dotenv

load_dotenv()

# ─── THREADS API ───────────────────────────────────────────
THREADS_USER_ID     = os.getenv("THREADS_USER_ID", "")       # ID akun Threads kamu
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "") # Token dari Meta Developer

# ─── HARGA API ─────────────────────────────────────────────
# Gunakan salah satu (pilih yang kamu punya API key-nya):
# Option A: Goldapi.io (recommended, gratis 100 req/bulan)
GOLD_API_KEY        = os.getenv("GOLD_API_KEY", "")
GOLD_API_URL        = "https://www.goldapi.io/api/XAU/USD"

# Option B: ExchangeRate API untuk kurs USD/IDR
EXCHANGE_API_KEY    = os.getenv("EXCHANGE_API_KEY", "")
EXCHANGE_API_URL    = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/USD/IDR"

# ─── KONSTANTA ANTAM ───────────────────────────────────────
# Formula: Harga Antam = (harga spot XAU/gram) × faktor markup Antam
ANTAM_JUAL_MARKUP   = 1.10   # +10% dari harga spot (sesuaikan dengan kondisi pasar)
ANTAM_BUYBACK_MARKUP = 1.02 # +2% dari harga spot

# ─── IMAGE CONFIG ──────────────────────────────────────────
TEMPLATE_PATH       = "template/chart_bg.png"
OUTPUT_PATH         = "output/latest.png"
IMAGE_WIDTH         = 1080
IMAGE_HEIGHT        = 400

# Font (download dari Google Fonts: Inter atau Roboto)
FONT_PATH_BOLD      = "fonts/Inter-Bold.ttf"
FONT_PATH_REGULAR   = "fonts/Inter-Regular.ttf"

# ─── SCHEDULER ─────────────────────────────────────────────
INTERVAL_MINUTES    = 15  # Post setiap 15 menit

# ─── WARNA ─────────────────────────────────────────────────
COLOR_BG            = (13, 17, 23)       # Dark background
COLOR_WHITE         = (255, 255, 255)
COLOR_RED           = (220, 60, 60)
COLOR_GREEN         = (50, 200, 100)
COLOR_YELLOW        = (255, 200, 50)
COLOR_GRAY          = (160, 160, 160)
COLOR_ACCENT        = (240, 185, 11)     # Gold accent
