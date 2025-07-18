from instagrapi import Client
import random
import time
from datetime import datetime, timedelta
import os
import gc  # Garbage collection
import psutil  # RAM kullanımını izlemek için
import json

# HESAP VE PROXY AYARLARI
COOKIE_FILE = os.getenv("COOKIE_FILE", "session.json")  # Cookie dosyası yolu
PROXY_URL = os.getenv("PROXY_URL")  # Proxy URL'si (format: http://username:password@host:port)

# TAKIPÇI İSTEKLERİ İÇİN AYARLAR
ACCEPT_REQUESTS_TIME = "14:30"  # Takipçi isteklerinin kabul edileceği saat (HH:MM)
ACCEPT_REQUESTS_ENABLED = True  # Takipçi isteklerini kabul etme özelliği

# ÇALIŞMA SAATLERİ AYARLARI
WORK_START_TIME = "11:00"  # Botun çalışmaya başlayacağı saat (HH:MM)
WORK_END_TIME = "23:00"    # Botun çalışmayı durduracağı saat (HH:MM)
WORK_HOURS_ENABLED = True  # Çalışma saatleri kontrolü

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
    time.sleep(1)  # GC'nin tamamlanması için kısa bekleme

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
        
        # Proxy URL'sini parse et
        if proxy_url.startswith('http://'):
            proxy_type = 'http'
        elif proxy_url.startswith('https://'):
            proxy_type = 'https'
        else:
            print("❌ Desteklenmeyen proxy tipi. http:// veya https:// kullanın")
            return False
        
        # Proxy ayarlarını uygula
        cl.set_proxy(proxy_url)
        print(f"✅ Proxy ayarlandı: {proxy_type.upper()}")
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
        
        # Eğer bitiş saati başlangıç saatinden küçükse (örn: 22:00 - 09:00)
        if end_time <= start_time:
            return current_time >= start_time or current_time <= end_time
        else:
            return start_time <= current_time <= end_time
    except:
        return True

def get_next_working_time():
    """Bir sonraki çalışma saatini hesapla"""
    if not WORK_HOURS_ENABLED:
        return None
    
    try:
        now = datetime.now()
        start_hour, start_minute = map(int, WORK_START_TIME.split(':'))
        
        next_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # Eğer bugünkü çalışma saati geçmişse, yarın için ayarla
        if next_start <= now:
            next_start += timedelta(days=1)
        
        return next_start
    except:
        return None

def safe_login():
    """Güvenli giriş - sadece cookie kullanımı + session sağlığı kontrolü + loglama"""
    try:
        print("🔐 Client başlatılıyor...")
        cl = Client()
        
        # Proxy kullanılıyorsa ayarla
        if PROXY_URL:
            print(f"🌐 Proxy ayarlanıyor: {PROXY_URL[:30]}...")
            if not setup_proxy(cl, PROXY_URL):
                raise Exception("Proxy ayarlanamadı veya geçersiz.")

        # Session dosyası yükleniyor
        print(f"📁 Session yükleniyor: {COOKIE_FILE}")
        session_loaded = load_session(cl, COOKIE_FILE)
        if not session_loaded:
            raise Exception(f"Session dosyası yüklenemedi veya eksik: {COOKIE_FILE}")

        # Session geçerli mi? Test et
        print("🔎 Session geçerliliği test ediliyor (account_info)...")
        try:
            account_info = cl.account_info()
            print(f"✅ Cookie ile giriş BAŞARILI → @{account_info.username} (ID: {account_info.pk})")
            return cl
        except Exception as e:
            print(f"❌ Session GEÇERSİZ — {type(e).__name__}: {str(e)[:300]}")
            raise Exception("Session geçersiz, cookie dosyası hatalı veya süresi dolmuş.")

    except Exception as e:
        print(f"🚫 Giriş başarısız — {type(e).__name__}: {str(e)[:300]}")
        raise e


def is_target_time(target_time_str):
    """Belirtilen saatin gelip gelmediğini kontrol et"""
    try:
        now = datetime.now()
        target_hour, target_minute = map(int, target_time_str.split(':'))
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # Eğer hedef saat geçmişse, yarın için ayarla
        if target_time < now:
            target_time += timedelta(days=1)
        
        # Hedef saate 2 dakika veya daha az kaldıysa True döndür
        time_diff = (target_time - now).total_seconds()
        return time_diff <= 120  # 2 dakika = 120 saniye
    except:
        return False

def accept_follow_requests(cl):
    """Tüm takipçi isteklerini doğal delaylerle kabul et - Memory optimized"""
    try:
        print("🔍 Takipçi istekleri kontrol ediliyor...")
        mem_before = get_memory_usage()
        
        # Takipçi isteklerini al
        pending_requests = cl.user_followers_pending()
        
        if not pending_requests:
            print("📭 Bekleyen takipçi isteği yok")
            return 0
        
        total_requests = len(pending_requests)
        accepted_count = 0
        print(f"📬 {total_requests} takipçi isteği bulundu")
        
        # Eğer çok fazla istek varsa, bellek tasarrufu için küçük gruplara böl
        batch_size = 10 if total_requests > 50 else total_requests
        
        for i in range(0, total_requests, batch_size):
            batch = pending_requests[i:i+batch_size]
            print(f"📦 Batch {i//batch_size + 1}/{(total_requests + batch_size - 1)//batch_size} işleniyor...")
            
            for j, user in enumerate(batch):
                try:
                    # RAM kontrolü - her 5 istekte bir
                    if (i + j) % 5 == 0:
                        current_mem = get_memory_usage()
                        if current_mem > 600:  # 600MB üzerinde
                            print(f"⚠️ RAM yüksek ({current_mem:.1f}MB) - kısa bellek temizleme...")
                            force_garbage_collection()
                    
                    # Takipçi isteğini kabul et
                    cl.user_following_approve(user.pk)
                    accepted_count += 1
                    print(f"✅ [{accepted_count}/{total_requests}] @{user.username} kabul edildi")
                    
                    # Doğal insan davranışı için değişken delayler
                    if accepted_count % 3 == 0:
                        # Her 3 istekte bir daha uzun bekleme
                        delay = random.randint(8, 15)
                        print(f"⏳ Ara bekleme: {delay} saniye")
                    else:
                        # Normal bekleme
                        delay = random.randint(3, 7)
                    
                    time.sleep(delay)
                    
                    # Her 10 istekte bir ekstra bekleme (bot olmamak için)
                    if accepted_count % 10 == 0 and accepted_count < total_requests:
                        extra_delay = random.randint(15, 30)
                        print(f"⏳ 10 istek sonrası ekstra bekleme: {extra_delay} saniye")
                        time.sleep(extra_delay)
                    
                except Exception as e:
                    print(f"❌ @{user.username} isteği kabul edilemedi: {str(e)[:50]}")
                    # Hata durumunda da kısa bekleme
                    time.sleep(random.randint(2, 5))
                    continue
            
            # Batch sonrası bellek temizleme
            if i + batch_size < total_requests:
                force_garbage_collection()
                batch_delay = random.randint(20, 40)
                print(f"⏳ Batch arası bekleme: {batch_delay} saniye")
                time.sleep(batch_delay)
        
        # Son bellek temizleme
        force_garbage_collection()
        mem_after = get_memory_usage()
        
        print(f"🎉 Toplam {accepted_count}/{total_requests} takipçi isteği kabul edildi!")
        print(f"📊 RAM kullanımı: {mem_before:.1f}MB → {mem_after:.1f}MB (Δ{mem_after-mem_before:+.1f}MB)")
        
        return accepted_count
        
    except Exception as e:
        print(f"❌ Takipçi istekleri işlenirken hata: {str(e)[:100]}")
        force_garbage_collection()  # Hata durumunda da bellek temizle
        return 0

def check_and_accept_requests(cl):
    """Saati kontrol et ve takipçi isteklerini doğal şekilde kabul et"""
    if not ACCEPT_REQUESTS_ENABLED:
        return
    
    if is_target_time(ACCEPT_REQUESTS_TIME):
        print(f"🕒 Hedef saat ({ACCEPT_REQUESTS_TIME}) geldi! Takipçi istekleri doğal delaylerle kabul ediliyor...")
        
        # Başlangıç bellek durumu
        mem_start = get_memory_usage()
        print(f"🧠 İşlem öncesi RAM: {mem_start:.1f}MB")
        
        # Takipçi isteklerini kabul et
        accepted = accept_follow_requests(cl)
        
        if accepted > 0:
            print(f"🎊 {accepted} takipçi isteği başarıyla kabul edildi!")
            
            # Tüm işlem sonrası ekstra bekleme (bot olmamak için)
            final_delay = random.randint(60, 120)
            print(f"⏳ Takipçi işlemi sonrası son bekleme: {final_delay} saniye")
            time.sleep(final_delay)
        
        # İşlem sonrası bellek durumu
        mem_end = get_memory_usage()
        print(f"🧠 İşlem sonrası RAM: {mem_end:.1f}MB")
        
        # Son bellek temizleme
        force_garbage_collection()
        
        # Session'ı güncelle
        save_session(cl, COOKIE_FILE)
        
        # İşlem tamamlandıktan sonra bir sonraki hedef zamanı bildir
        next_target = get_next_target_time()
        if next_target:
            print(f"📅 Bir sonraki takipçi kontrolü: {next_target.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("=" * 50)

def comment_to_user(cl, username):
    """Belirtilen kullanıcıya yorum at - bellek optimizasyonu ile"""
    try:
        mem_before = get_memory_usage()
        print(f"📌 @{username} için işlem başlatıldı...")

        if random.random() < 0.1:
            print(f"⏭️ @{username} atlandı (rastgele skip)")
            return False

        try:
            print(f"🔍 @{username} kullanıcı ID'si aranıyor...")
            results = cl.search_users(username)
            if not results:
                print(f"⚠️ @{username} kullanıcısı bulunamadı (search_users boş)")
                return False
            user_id = results[0].pk
            print(f"✅ Kullanıcı ID bulundu: {user_id}")
        except Exception as e:
            print(f"❌ @{username} kullanıcı arama hatası: {e}")
            return False

        try:
            print(f"📥 @{username} için medya verisi alınıyor...")
            medias = cl.user_medias(user_id, amount=1)
        except Exception as e:
            print(f"❌ Medya çekme hatası: {e}")
            return False

        if not medias:
            print(f"⚠️ @{username} için hiç gönderi bulunamadı")
            return False

        try:
            media_id = medias[0].id
            comment = get_random_comment()
            print(f"💬 Yorum atılıyor: \"{comment}\"")
            cl.media_comment(media_id, comment)
            print(f"✅ Yorum başarıyla atıldı: {comment}")
            del medias, media_id
            mem_after = get_memory_usage()
            print(f"📊 RAM: {mem_after:.1f}MB (Δ{mem_after - mem_before:+.1f}MB)")
            return True
        except Exception as e:
            print(f"❌ Yorum atma hatası: {type(e).__name__} → {str(e)[:500]}")
            return False

    except Exception as e:
        print(f"❌ Genel hata (@{username}): {type(e).__name__} → {str(e)[:100]}")
        return False

    finally:
        force_garbage_collection()


def run_comment_cycle(cl):
    """Tüm sayfalara yorum atma döngüsü - bellek optimizasyonu ile"""
    # Target userları karıştır
    shuffled_users = random.sample(target_users, len(target_users))
    
    print(f"🎯 Bu döngüde {len(shuffled_users)} sayfaya yorum atılacak...")
    print(f"🧠 Başlangıç RAM: {get_memory_usage():.1f}MB")
    
    successful_comments = 0
    
    for i, username in enumerate(shuffled_users):
        # Çalışma saatleri kontrolü
        if not is_working_hours():
            print(f"⏰ Çalışma saatleri dışında - işlem durduruldu")
            break
        
        print(f"\n📍 [{i+1}/{len(shuffled_users)}] @{username} işleniyor...")
        
        # Her kullanıcı işlemi öncesi takipçi isteklerini kontrol et
        check_and_accept_requests(cl)
        
        # RAM kontrolü - %80'i aşarsa garbage collection
        current_mem = get_memory_usage()
        if current_mem > 800:  # 800MB üzerinde
            print(f"⚠️ RAM yüksek ({current_mem:.1f}MB) - bellek temizleniyor...")
            force_garbage_collection()
            time.sleep(2)
        
        # Yorum at
        success = comment_to_user(cl, username)
        if success:
            successful_comments += 1
        
        # Son kullanıcı değilse sayfalar arası bekleme
        if i < len(shuffled_users) - 1:
            inter_delay = random.randint(60, 180)  # 1-3 dakika
            print(f"⏳ Sonraki sayfaya kadar bekleme: {inter_delay // 60} dakika {inter_delay % 60} saniye")
            time.sleep(inter_delay)
        
        # Hata durumunda ek bekleme
        if not success:
            extra_delay = random.randint(30, 90)
            print(f"⏳ Hata sonrası ek bekleme: {extra_delay} saniye")
            time.sleep(extra_delay)
    
    # Session'ı güncelle
    save_session(cl, COOKIE_FILE)
    
    # Sadece bellek temizleme
    force_garbage_collection()
    
    final_mem = get_memory_usage()
    print(f"\n📊 Döngü özeti: {successful_comments}/{len(shuffled_users)} başarılı yorum")
    print(f"🧠 Son RAM: {final_mem:.1f}MB")
    
    return successful_comments

def check_session_health(cl):
    """Session sağlığını kontrol et"""
    try:
        # Basit bir API çağrısı ile session'ı test et
        cl.account_info()
        return True
    except Exception as e:
        print(f"⚠️ Session sorunu tespit edildi: {str(e)[:50]}...")
        return False

def get_next_target_time():
    """Bir sonraki hedef saati hesapla"""
    try:
        now = datetime.now()
        target_hour, target_minute = map(int, ACCEPT_REQUESTS_TIME.split(':'))
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # Eğer hedef saat geçmişse, yarın için ayarla
        if target_time < now:
            target_time += timedelta(days=1)
        
        return target_time
    except:
        return None

def wait_for_working_hours():
    """Çalışma saatleri başlayana kadar bekle"""
    if not WORK_HOURS_ENABLED:
        return
    
    while not is_working_hours():
        next_work_time = get_next_working_time()
        if next_work_time:
            now = datetime.now()
            wait_seconds = (next_work_time - now).total_seconds()
            wait_hours = int(wait_seconds // 3600)
            wait_minutes = int((wait_seconds % 3600) // 60)
            
            print(f"⏰ Çalışma saatleri dışında ({WORK_START_TIME} - {WORK_END_TIME})")
            print(f"🕒 Sonraki çalışma saati: {next_work_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳ Bekleme süresi: {wait_hours} saat {wait_minutes} dakika")
            
            # Her 30 dakikada bir durum kontrolü
            while wait_seconds > 0 and not is_working_hours():
                sleep_time = min(1800, wait_seconds)  # 30 dakika veya kalan süre
                time.sleep(sleep_time)
                wait_seconds -= sleep_time
                
                if wait_seconds > 0:
                    wait_hours = int(wait_seconds // 3600)
                    wait_minutes = int((wait_seconds % 3600) // 60)
                    print(f"⏳ Kalan bekleme: {wait_hours} saat {wait_minutes} dakika")

def run_comment_loop():
    """Ana döngü - sadece cookie kullanımı + çalışma saatleri kontrolü"""
    loop_count = 0
    cl = None
    
    # İlk giriş
    try:
        cl = safe_login()
    except Exception as e:
        print(f"❌ Cookie ile giriş başarısız: {str(e)}")
        print("📝 Lütfen session.json dosyasını kontrol edin")
        return

    # Çalışma saatleri bilgisini göster
    if WORK_HOURS_ENABLED:
        print(f"⏰ Çalışma saatleri: {WORK_START_TIME} - {WORK_END_TIME}")
    else:
        print("⏰ Çalışma saatleri kontrolü kapalı - 7/24 çalışır")
    
    # Takipçi istekleri bilgisini göster
    if ACCEPT_REQUESTS_ENABLED:
        next_target = get_next_target_time()
        if next_target:
            print(f"🕒 Takipçi istekleri {ACCEPT_REQUESTS_TIME} saatinde kabul edilecek")
            print(f"📅 Sonraki hedef: {next_target.strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
        # Çalışma saatleri kontrolü
        wait_for_working_hours()
        
        # Eğer çalışma saatleri dışındaysa döngüyü devam ettir
        if not is_working_hours():
            continue
        
        loop_count += 1
        print(f"\n🔄 ===== DÖNGÜ #{loop_count} BAŞLIYOR ===== @ {datetime.now().strftime('%H:%M:%S')}")

        # Session sağlığını kontrol et
        if not check_session_health(cl):
            print("🔄 Session yenileniyor...")
            try:
                cl = safe_login()
            except Exception as e:
                print(f"❌ Session yenileme başarısız: {str(e)}")
                time.sleep(600)  # 10 dakika bekle
                continue

        # Döngü başında takipçi isteklerini kontrol et
        check_and_accept_requests(cl)

        # Sistem bellek kontrolü
        try:
            system_mem = psutil.virtual_memory()
            print(f"🖥️ Sistem RAM: {system_mem.percent}% kullanılıyor")
            
            if system_mem.percent > 90:
                print("⚠️ Sistem RAM'i yüksek - 2 dakika bekleme...")
                time.sleep(120)
        except:
            pass

        # Tüm sayfalara yorum at
        cycle_start = time.time()
        try:
            successful_comments = run_comment_cycle(cl)
        except Exception as e:
            print(f"❌ Döngü hatası: {str(e)[:100]}")
            successful_comments = 0
            # Hata durumunda session'ı yenile
            print("🔄 Hata sonrası session yenileniyor...")
            try:
                cl = safe_login()
            except:
                print("❌ Session yenileme başarısız")
            time.sleep(300)  # 5 dakika
        
        cycle_end = time.time()
        cycle_duration = cycle_end - cycle_start
        
        print(f"\n✅ Döngü #{loop_count} tamamlandı!")
        print(f"📊 Başarılı yorum: {successful_comments}/{len(target_users)}")
        print(f"⏱️ Süre: {cycle_duration // 60:.0f} dakika {cycle_duration % 60:.0f} saniye")

        # Takipçi istekleri durumunu göster
        if ACCEPT_REQUESTS_ENABLED:
            next_target = get_next_target_time()
            if next_target:
                time_until_target = (next_target - datetime.now()).total_seconds()
                if time_until_target > 0:
                    hours = int(time_until_target // 3600)
                    minutes = int((time_until_target % 3600) // 60)
                    print(f"🕒 Takipçi istekleri kontrolüne {hours}s {minutes}dk kaldı")

        # Ana döngü bekleme süresi (60-90 dakika)
        main_delay = random.randint(3600, 5400)  # 60–90 dakika
        print(f"⏰ Sonraki döngüye kadar bekleme: {main_delay // 60} dakika")
        print(f"🕒 Sonraki döngü tahmini: {datetime.fromtimestamp(time.time() + main_delay).strftime('%H:%M:%S')}")
        print("=" * 50)
        
        # Bekleme sırasında bellek temizleme
        force_garbage_collection()
        
        # Bekleme sırasında takipçi isteklerini ve çalışma saatlerini kontrol et
        sleep_intervals = 600  # 10 dakika aralıklar
        remaining_time = main_delay
        
        while remaining_time > 0:
            # Çalışma saatleri kontrolü
            if not is_working_hours():
                print("⏰ Çalışma saatleri dışına çıkıldı - döngü sonlandırılıyor")
                break
            
            sleep_time = min(sleep_intervals, remaining_time)
            time.sleep(sleep_time)
            remaining_time -= sleep_time
            
            # Her 10 dakikada bir takipçi isteklerini kontrol et
            if remaining_time > 0:
                check_and_accept_requests(cl)
                
                # Takipçi kontrolü sonrası bellek temizleme
                if remaining_time > 300:  # 5 dakikadan fazla kaldıysa
                    force_garbage_collection()

# ▶️ BAŞLAT
if __name__ == "__main__":
   print("🤖 Instagram Comment Bot - Cookie Only & Working Hours")
   print("📋 Hedef sayfalar:")
   for i, user in enumerate(target_users, 1):
       print(f"   {i}. @{user}")
   
   print(f"\n🍪 Cookie ayarları:")
   print(f"   📁 Cookie dosyası: {COOKIE_FILE}")
   print(f"   ✅ Cookie giriş: {'Aktif' if os.path.exists(COOKIE_FILE) else 'Pasif (dosya yok)'}")
   
   print(f"\n🕒 Çalışma saatleri ayarları:")
   print(f"   ⏰ Çalışma saatleri: {WORK_START_TIME} - {WORK_END_TIME}")
   print(f"   🔄 Çalışma saatleri kontrolü: {'Aktif' if WORK_HOURS_ENABLED else 'Pasif'}")
   
   print(f"\n👥 Takipçi istekleri ayarları:")
   print(f"   🕒 Kabul saati: {ACCEPT_REQUESTS_TIME}")
   print(f"   ✅ Takipçi istekleri: {'Aktif' if ACCEPT_REQUESTS_ENABLED else 'Pasif'}")
   
   print(f"\n🌐 Proxy ayarları:")
   print(f"   🔗 Proxy: {'Aktif' if PROXY_URL else 'Pasif'}")
   if PROXY_URL:
       print(f"   📡 URL: {PROXY_URL[:20]}...")
   
   print(f"\n💬 Yorum havuzu: {len(comments_pool)} farklı yorum")
   print(f"🎯 Hedef sayfa sayısı: {len(target_users)}")
   
   print("\n" + "="*50)
   print("🚀 Bot başlatılıyor...")
   print("="*50)
   
   try:
       run_comment_loop()
   except KeyboardInterrupt:
       print("\n\n⛔ Bot durduruldu (Ctrl+C)")
   except Exception as e:
       print(f"\n\n❌ Beklenmeyen hata: {str(e)}")
   finally:
       print("🔄 Bellek temizleniyor...")
       force_garbage_collection()
       print("👋 Bot kapatılıyor...")