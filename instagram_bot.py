from instagrapi import Client
import random
import time
from datetime import datetime, timedelta
import os
import gc
import psutil
import json

# HESAP VE PROXY AYARLARI
COOKIE_FILE = os.getenv("COOKIE_FILE", "session.json")
PROXY_URL = os.getenv("PROXY_URL")

# TAKIPÇI İSTEKLERİ İÇİN AYARLAR
ACCEPT_REQUESTS_TIME = "14:30"
ACCEPT_REQUESTS_ENABLED = True

# ÇALIŞMA SAATLERİ AYARLARI
WORK_START_TIME = "11:00"
WORK_END_TIME = "23:00"
WORK_HOURS_ENABLED = True

# Her kullanıcı için farklı random davranış için seed ayarla
random.seed(time.time())

target_users = [
    "sevgili_bulma_tanisma_grubu",
    "arkadaslik_sohbet_sayfasi_van",
    "arkadas_ekleme_sayfasss00",
    "arkadas_ekleme_sayfass00",
    "arkadas_ekleme_sayfa00",
    "_arkadas_ekleme_sayfasi",
    "arkadas_ekleme_sayfasi_1",
    "kismet.bul"
]

comments_pool = [
    "💅✨", "💄🌸", "💫🫦", "🪞🌟", "💁‍♀️🎀", "👠💅", "🌸💫", "💄🌟",
    "🫦💁‍♀️", "🎀👠", "💅🌸", "✨💄", "🌟🫦", "💁‍♀️🪞", "🎀💫",
    "güzel", "merhaba", "harika", "ankara", "süper", "👏", "🔥", "💖", "😍", "🥰", "❤️", "slm",
    "tatlı", "ciddi", "💕", "🌺", "✨", "💐", "🌹", "💜", "🧡",
    "Selammmm💅", "harika 🌸", "süper ✨", "mükemmel 💫", "tatlı 🎀",
    "güzel paylaşım 💄", "beğendim 🌟", "çok tatlı 💁‍♀️", "harika 👠"
]

def get_random_comment():
    return random.choice(comments_pool)

def get_memory_usage():
    """RAM kullanımını döndür (MB)"""
    try:
        return psutil.Process().memory_info().rss / 1024 / 1024
    except:
        return 0

def force_garbage_collection():
    """Manuel garbage collection ve bellek temizleme"""
    gc.collect()
    time.sleep(1)

def load_session(cl, filename):
    """Session'ı dosyadan yükle"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Session dosyası bulunamadı: {filename}")
            print("📝 Lütfen session.json dosyasını oluşturun ve Instagram cookie verilerinizi ekleyin")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        cl.set_settings(session_data)
        print(f"✅ Session yüklendi: {filename}")
        return True
    except Exception as e:
        print(f"❌ Session yüklenemedi: {str(e)[:100]}")
        return False

def save_session(cl, filename):
    """Session'ı dosyaya kaydet"""
    try:
        session_data = cl.get_settings()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Session kaydedildi: {filename}")
        return True
    except Exception as e:
        print(f"❌ Session kaydedilemedi: {str(e)[:100]}")
        return False

def setup_proxy(cl, proxy_url):
    """Proxy ayarlarını yapılandır"""
    try:
        if not proxy_url:
            print("⚠️ Proxy URL'si belirtilmedi")
            return False
        
        # Proxy formatını kontrol et
        if not (proxy_url.startswith('http://') or proxy_url.startswith('https://')):
            print("❌ Proxy format hatası. Örnek: http://username:password@ip:port")
            return False
        
        # Proxy ayarlarını uygula
        cl.set_proxy(proxy_url)
        print(f"✅ Proxy ayarlandı")
        return True
    except Exception as e:
        print(f"❌ Proxy ayarlanamadı: {str(e)[:100]}")
        return False

def is_working_hours():
    """Çalışma saatleri içinde olup olmadığını kontrol et"""
    if not WORK_HOURS_ENABLED:
        return True
    
    try:
        now = datetime.now()
        current_time = now.time()
        
        start_hour, start_minute = map(int, WORK_START_TIME.split(':'))
        end_hour, end_minute = map(int, WORK_END_TIME.split(':'))
        
        start_time = datetime.strptime(f"{start_hour}:{start_minute}", "%H:%M").time()
        end_time = datetime.strptime(f"{end_hour}:{end_minute}", "%H:%M").time()
        
        if end_time <= start_time:
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time
    except:
        return True

def safe_login():
    """Güvenli giriş - session tabanlı"""
    try:
        print("🔐 Client başlatılıyor...")
        
        # Client'ı request/response delay'leri ile başlat
        cl = Client()
        cl.delay_range = [1, 3]  # Request arası delay
        
        # Proxy kullanılıyorsa ayarla
        if PROXY_URL:
            print(f"🌐 Proxy ayarlanıyor...")
            if not setup_proxy(cl, PROXY_URL):
                print("⚠️ Proxy ayarlanamadı, proxy'siz devam ediliyor")

        # Session dosyası yükleniyor
        print(f"📁 Session yükleniyor: {COOKIE_FILE}")
        session_loaded = load_session(cl, COOKIE_FILE)
        if not session_loaded:
            raise Exception(f"Session dosyası yüklenemedi: {COOKIE_FILE}")

        # Session geçerliliği testi
        print("🔎 Session geçerliliği test ediliyor...")
        try:
            account_info = cl.account_info()
            print(f"✅ Giriş BAŞARILI → @{account_info.username}")
            
            # Session'ı güncelle
            save_session(cl, COOKIE_FILE)
            return cl
            
        except Exception as e:
            print(f"❌ Session geçersiz: {str(e)[:150]}")
            raise Exception("Session geçersiz, cookie'leri güncellemeniz gerekiyor")

    except Exception as e:
        print(f"🚫 Giriş başarısız: {str(e)[:200]}")
        raise e

def comment_to_user(cl, username):
    """Kullanıcıya yorum at - geliştirilmiş hata kontrolü"""
    try:
        print(f"📌 @{username} için işlem başlatıldı...")

        # %10 ihtimalle skip (doğal davranış)
        if random.random() < 0.1:
            print(f"⏭️ @{username} rastgele atlandı")
            return False

        # Kullanıcı arama
        try:
            print(f"🔍 @{username} aranıyor...")
            user_info = cl.user_info_by_username(username)
            user_id = user_info.pk
            print(f"✅ Kullanıcı bulundu: {user_id}")
        except Exception as e:
            print(f"❌ Kullanıcı bulunamadı: {str(e)[:100]}")
            return False

        # Kullanıcının gönderilerini al
        try:
            print(f"📥 @{username} gönderileri alınıyor...")
            medias = cl.user_medias(user_id, amount=5)  # 5 gönderi al
            
            if not medias:
                print(f"⚠️ @{username} hiç gönderi yok")
                return False
                
            # En son gönderiye yorum at
            media = medias[0]
            print(f"📝 Gönderi bulundu: {media.id}")
            
        except Exception as e:
            print(f"❌ Gönderi alınamadı: {str(e)[:100]}")
            return False

        # Yorum at
        try:
            comment = get_random_comment()
            print(f"💬 Yorum atılıyor: \"{comment}\"")
            
            # Yorum atma
            cl.media_comment(media.id, comment)
            
            print(f"✅ Yorum başarıyla atıldı!")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ Yorum atılamadı: {str(e)[:200]}")
            
            # Hata tipine göre farklı davranış
            if "challenge" in error_msg or "login" in error_msg:
                print("⚠️ Challenge/Login hatası - session yenilenmesi gerekiyor")
                raise Exception("Session challenge")
            elif "rate limit" in error_msg or "spam" in error_msg:
                print("⚠️ Rate limit - daha uzun bekleme gerekiyor")
                time.sleep(random.randint(300, 600))  # 5-10 dakika
            elif "private" in error_msg:
                print("⚠️ Hesap private - atlanıyor")
            
            return False

    except Exception as e:
        print(f"❌ Genel hata: {str(e)[:100]}")
        return False
    
    finally:
        # Bellek temizleme
        force_garbage_collection()

def run_comment_cycle(cl):
    """Yorum atma döngüsü"""
    shuffled_users = random.sample(target_users, len(target_users))
    
    print(f"🎯 {len(shuffled_users)} sayfaya yorum atılacak...")
    
    successful_comments = 0
    
    for i, username in enumerate(shuffled_users):
        # Çalışma saatleri kontrolü
        if not is_working_hours():
            print(f"⏰ Çalışma saatleri dışında - döngü durduruluyor")
            break
        
        print(f"\n📍 [{i+1}/{len(shuffled_users)}] @{username}")
        
        # Yorum at
        try:
            success = comment_to_user(cl, username)
            if success:
                successful_comments += 1
                
        except Exception as e:
            if "challenge" in str(e).lower():
                print("🔄 Challenge hatası - session yenilenmesi gerekiyor")
                raise e
            print(f"❌ Kullanıcı işlem hatası: {str(e)[:100]}")
        
        # Sayfalar arası bekleme
        if i < len(shuffled_users) - 1:
            # Başarılı yorum sonrası daha az bekleme
            if successful_comments > 0:
                delay = random.randint(45, 120)  # 45 saniye - 2 dakika
            else:
                delay = random.randint(60, 180)  # 1-3 dakika
                
            print(f"⏳ Bekleme: {delay} saniye")
            time.sleep(delay)
    
    print(f"\n📊 Döngü sonucu: {successful_comments}/{len(shuffled_users)} başarılı")
    return successful_comments

def check_session_health(cl):
    """Session sağlığını kontrol et"""
    try:
        cl.account_info()
        return True
    except Exception as e:
        print(f"⚠️ Session problemi: {str(e)[:100]}")
        return False

def run_comment_loop():
    """Ana döngü"""
    loop_count = 0
    cl = None
    
    # İlk giriş
    try:
        cl = safe_login()
    except Exception as e:
        print(f"❌ İlk giriş başarısız: {str(e)}")
        return

    print(f"⏰ Çalışma saatleri: {WORK_START_TIME} - {WORK_END_TIME}")
    print(f"🎯 Hedef sayfa sayısı: {len(target_users)}")
    
    while True:
        # Çalışma saatleri kontrolü
        if not is_working_hours():
            print("⏰ Çalışma saatleri dışında - bekleniyor...")
            time.sleep(1800)  # 30 dakika bekle
            continue
        
        loop_count += 1
        print(f"\n🔄 ===== DÖNGÜ #{loop_count} ===== @ {datetime.now().strftime('%H:%M:%S')}")

        # Session sağlığı kontrolü
        if not check_session_health(cl):
            print("🔄 Session yenileniyor...")
            try:
                cl = safe_login()
            except Exception as e:
                print(f"❌ Session yenileme başarısız: {str(e)}")
                time.sleep(600)  # 10 dakika bekle
                continue

        # Yorum döngüsü
        try:
            successful_comments = run_comment_cycle(cl)
            print(f"✅ Döngü #{loop_count} tamamlandı: {successful_comments} yorum")
            
        except Exception as e:
            print(f"❌ Döngü hatası: {str(e)}")
            # Challenge/session hatası varsa session yenile
            if "challenge" in str(e).lower():
                try:
                    cl = safe_login()
                except:
                    print("❌ Session yenileme başarısız")
                    time.sleep(600)
                    continue
            time.sleep(300)  # 5 dakika bekle
            continue

        # Ana bekleme (45-75 dakika)
        main_delay = random.randint(2700, 4500)  # 45-75 dakika
        print(f"⏰ Sonraki döngüye kadar: {main_delay // 60} dakika")
        print(f"🕒 Sonraki döngü: {datetime.fromtimestamp(time.time() + main_delay).strftime('%H:%M:%S')}")
        
        # Bellek temizleme
        force_garbage_collection()
        
        # Bekleme
        time.sleep(main_delay)

# Test fonksiyonu
def test_single_comment():
    """Tek yorum testi"""
    print("🧪 Tek yorum testi başlatılıyor...")
    
    try:
        cl = safe_login()
        test_user = random.choice(target_users)
        print(f"🎯 Test kullanıcısı: @{test_user}")
        
        success = comment_to_user(cl, test_user)
        
        if success:
            print("✅ Test başarılı!")
        else:
            print("❌ Test başarısız!")
            
    except Exception as e:
        print(f"❌ Test hatası: {str(e)}")

# ▶️ BAŞLAT
if __name__ == "__main__":
    print("🤖 Instagram Comment Bot v2.0")
    print("📋 Hedef sayfalar:")
    for i, user in enumerate(target_users, 1):
        print(f"   {i}. @{user}")
    
    print(f"\n🍪 Session dosyası: {COOKIE_FILE}")
    print(f"🌐 Proxy: {'Aktif' if PROXY_URL else 'Pasif'}")
    print(f"💬 Yorum sayısı: {len(comments_pool)}")
    
    print("\n" + "="*50)
    
    # Kullanıcıya seçenek sun
    print("Seçenekler:")
    print("1. Normal bot başlat")
    print("2. Tek yorum testi")
    
    choice = input("\nSeçiminiz (1-2): ").strip()
    
    if choice == "2":
        test_single_comment()
    else:
        print("🚀 Bot başlatılıyor...")
        try:
            run_comment_loop()
        except KeyboardInterrupt:
            print("\n⛔ Bot durduruldu")
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {str(e)}")
        finally:
            print("👋 Bot kapatılıyor...")
            force_garbage_collection()