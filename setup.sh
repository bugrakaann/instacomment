#!/bin/bash

# Instagram Bot Docker Setup Script
# Bu script'i çalıştırarak tüm kurulumu otomatik yap

echo "🤖 Instagram Bot Docker Setup"
echo "================================"

# Gerekli klasörleri oluştur
echo "📁 Klasörler oluşturuluyor..."
mkdir -p logs sessions

# Klasör izinlerini ayarla
chmod 755 logs sessions

# Docker'ın kurulu olup olmadığını kontrol et
if ! command -v docker &> /dev/null; then
    echo "❌ Docker kurulu değil! Lütfen Docker'ı kurun."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose kurulu değil! Lütfen Docker Compose'u kurun."
    exit 1
fi

echo "✅ Docker ve Docker Compose kurulu."

# Docker image'i build et
echo "🏗️ Docker image build ediliyor..."
docker-compose build

# Container'ı çalıştır
echo "🚀 Bot başlatılıyor..."
docker-compose up -d

# Durum kontrolü
echo "📊 Container durumu:"
docker-compose ps

echo ""
echo "🎉 Kurulum tamamlandı!"
echo ""
echo "📋 Kullanışlı komutlar:"
echo "  Logları görüntüle:    docker-compose logs -f"
echo "  Bot'u durdur:         docker-compose down"
echo "  Bot'u yeniden başlat: docker-compose restart"
echo "  Durum kontrol:        docker-compose ps"
echo ""
echo "⚠️ Bot arkaplanda çalışmaya başladı!"
echo "📝 Logları takip etmek için: docker-compose logs -f"