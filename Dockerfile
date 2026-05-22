# استخدام نسخة بايثون مستقرة وخفيفة
FROM python:3.10-slim

# تحديث مستودعات الحزم وتثبيت أداة ffmpeg الأساسية لمعالجة وتدفق الصوت
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع إلى الحاوية
COPY . .

# أمر تشغيل السكربت لضمان استمراريته
CMD ["python", "app.py"]
