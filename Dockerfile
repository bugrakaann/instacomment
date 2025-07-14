FROM python:3.10-slim

# Çalışma dizinini belirle
WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodları kopyala
COPY . .
ENV PYTHONUNBUFFERED=1

ENV USERNAME=default_user
ENV PASSWORD=default_pass
# Uygulamayı başlat
CMD ["python", "instagram_bot.py"]
