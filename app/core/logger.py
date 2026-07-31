
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Logların kaydedileceği klasörü oluştur
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log dosyasının yolu
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logger():
    # Temel logger nesnesini oluştur
    logger = logging.getLogger("medium_clone")
    logger.setLevel(logging.INFO) # INFO ve üzeri (WARNING, ERROR, CRITICAL) seviyeleri yakala

    # Log formatı: Tarih - İsim - Seviye - Mesaj
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Terminal  Çıktısı İçin Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    #  Dosya Çıktısı İçin Handler (Max 5MB boyut, dolarsa yeni dosyaya geçer - Rotating)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5000000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Handler'ları logger'a ekle
    # Eğer daha önce eklenmişse çift yazmayı engellemek için temizle
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Diğer dosyalardan import edebilmek için logger objesini oluşturuyoruz
logger = setup_logger()