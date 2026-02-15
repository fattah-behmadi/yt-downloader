# 🎬 YouTube Video Downloader

دانلودر سریع و ساده ویدیوهای یوتیوب با پشتیبانی از پلی‌لیست، دانلود صفی و تشخیص خودکار پروکسی. ساخته شده برای وقتی که فقط می‌خوای ویدیو رو بگیری و بری، نه اینکه با تنظیمات عجیب بجنگی.

---

## ✨ ویژگی‌ها

* ⚡ دانلود سریع با فرگمنت‌های همزمان
* 📋 پشتیبانی کامل از پلی‌لیست‌ها
* 🔗 دانلود تکی یا چندتایی
* 🌐 تشخیص خودکار پروکسی (V2Ray، Clash و موارد مشابه)
* 🎥 انتخاب کیفیت خروجی از 360p تا 1080p
* 🎵 دانلود فقط صدا
* 📊 نمایش پیشرفت، سرعت و زمان باقی‌مانده
* 📋 گزارش نهایی دانلودها
* 🔄 تلاش مجدد خودکار در صورت خطا
* 🚫 بدون نیاز به ffmpeg

---

## 📦 پیش‌نیازها

### 1. نصب Python (نسخه 3.10 یا بالاتر)

```bash
python --version
```

### 2. نصب uv (مدیر پکیج)

**Linux / macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. نصب وابستگی‌ها

```bash
uv sync
```

### 4. بررسی نصب صحیح

```bash
uv pip list
uv run python -c "import yt_dlp, rich; print('✅ نصب با موفقیت انجام شد')"
uv run yt-downloader --help
```

---

## 📝 آماده‌سازی لینک‌ها

لینک‌ها رو داخل فایل `links.txt` قرار بده:

```text
# ویدیوهای تکی
https://www.youtube.com/watch?v=VIDEO_ID_1
https://youtu.be/VIDEO_ID_2

# پلی‌لیست کامل
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxx

# یک ویدیو مشخص از پلی‌لیست
https://www.youtube.com/watch?v=xyz&list=PLxxxxxxx&index=5
```

---

## ▶️ اجرا

### دانلود از فایل لینک‌ها

```bash
uv run yt-downloader -f links.txt
```

### دانلود با لینک مستقیم

```bash
uv run yt-downloader -u "https://www.youtube.com/watch?v=VIDEO_ID"
```

### چند لینک مستقیم

```bash
uv run yt-downloader -u "https://youtube.com/watch?v=aaa" "https://youtube.com/watch?v=bbb"
```

---

## 🎥 انتخاب کیفیت خروجی

```bash
# 360p (کم‌حجم)
uv run yt-downloader -f links.txt --format "best[height<=360]/best"

# 720p (پیش‌فرض)
uv run yt-downloader -f links.txt

# 1080p (بالاترین کیفیت بدون ffmpeg)
uv run yt-downloader -f links.txt --format "best[height<=1080]/best"

# بهترین کیفیت موجود
uv run yt-downloader -f links.txt --format "best"
```

---

## 🎵 دانلود فقط صدا

```bash
uv run yt-downloader -f links.txt --format "bestaudio/best"
```

---

## ⚡ تنظیم سرعت دانلود

```bash
# پیش‌فرض (4 فرگمنت)
uv run yt-downloader -f links.txt

# سریع‌تر
uv run yt-downloader -f links.txt -j 8

# خیلی سریع (نیازمند اینترنت قوی)
uv run yt-downloader -f links.txt -j 16
```

---

## 🌐 تنظیم پروکسی

```bash
# تشخیص خودکار (پیش‌فرض)
uv run yt-downloader -f links.txt

# SOCKS5
uv run yt-downloader -f links.txt --proxy socks5://127.0.0.1:1080

# HTTP
uv run yt-downloader -f links.txt --proxy http://127.0.0.1:7890

# بدون پروکسی
uv run yt-downloader -f links.txt --no-proxy
```

---

## 📁 پوشه خروجی

```bash
# پیش‌فرض: ./downloads
uv run yt-downloader -f links.txt

# پوشه دلخواه
uv run yt-downloader -f links.txt -o ./my_videos

# مسیر کامل
uv run yt-downloader -f links.txt -o /home/user/Videos/youtube
```

---

## 🏆 مثال‌های پرکاربرد

```bash
# دانلود سریع 1080p
uv run yt-downloader -f links.txt -j 8 --format "best[height<=1080]/best"

# دانلود کم‌حجم برای موبایل
uv run yt-downloader -f links.txt --format "best[height<=360]/best" -o ./mobile

# دانلود یک ویدیو خاص
uv run yt-downloader -u "https://www.youtube.com/watch?v=VIDEO_ID" -j 8

# دانلود صدای یک پلی‌لیست
uv run yt-downloader -u "https://www.youtube.com/playlist?list=PLxxx" --format "bestaudio/best" -o ./music
```
