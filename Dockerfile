# 1. İşletim sistemi ve Python sürümü (Senin sisteminle aynı: 3.13)
FROM python:3.10-slim

# 2. Konteyner içindeki çalışma klasörümüz
WORKDIR /app

# 3. Önce gereksinim listesini kopyala ve kütüphaneleri kur
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

# 4. Projedeki tüm kodları konteynerin içine kopyala
COPY . .

# 5. Dışarıya açılacak port
EXPOSE 8000

# 6. Uygulamayı başlatma komutu
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
