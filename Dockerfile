# 1. İşletim sistemi ve Python sürümü
FROM python:3.10-slim

# 2. Konteyner içindeki çalışma klasörümüz
WORKDIR /app


# 3. ÖNCE ağır AI kütüphanelerini kuruyoruz! Bu katman Docker tarafından
# sonsuza kadar önbellekte tutulacak. (Eğer CPU kullanıyorsan aşağıdaki linki koru)
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir TTS
# -------------------------

# 4. Kalan normal gereksinimleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Projedeki tüm kodları kopyala
COPY . .

# 6. Dışarıya açılacak port
EXPOSE 8000

# 7. Uygulamayı başlatma komutu
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
