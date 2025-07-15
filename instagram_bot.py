from instagrapi import Client
import random
import time
from datetime import datetime, timedelta
import os
import gc  # Garbage collection
import psutil  # RAM kullanımını izlemek için

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# TAKIPÇI İSTEKLERİ İÇİN AYARLAR
ACCEPT_REQUESTS_TIME = "14:30"  # Takipçi isteklerinin kabul edileceği saat (HH:MM)
ACCEPT_REQUESTS_ENABLED = True  # Takipçi isteklerini kabul etme özelliği

# Her kullanıcı için farklı random davranış için seed ayarla
random.seed(time.time() + hash(USERNAME))

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

def safe_login():
    """Güvenli giriş - bağlantı sorunlarında yeniden dene"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            cl = Client()
            cl.login(USERNAME, PASSWORD)
            print(f"✅ Giriş başarılı @ {datetime.now().strftime('%H:%M:%S')}")
            return cl
        except Exception as e:
            print(f"❌ Giriş hatası (deneme {attempt+1}/{max_retries}): {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(30)  # 30 saniye bekle
            else:
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
        
        # İşlem tamamlandıktan sonra bir sonraki hedef zamanı bildir
        next_target = get_next_target_time()
        if next_target:
            print(f"📅 Bir sonraki takipçi kontrolü: {next_target.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("=" * 50)

def comment_to_user(cl, username):
    """Belirtilen kullanıcıya yorum at - bellek optimizasyonu ile"""
    try:
        mem_before = get_memory_usage()
        
        if random.random() < 0.1:  # %10 şansla skip
            print(f"⏭️ @{username} atlandı (rastgele skip)")
            return False
        
        # Kullanıcı ID'sini al
        try:
            user_id = cl.user_id_from_username(username)
        except Exception as e:
            print(f"⚠️ @{username} kullanıcısı bulunamadı")
            return False
        
        # Medyaları al - sadece 1 tane, daha az bellek kullanımı
        try:
            medias = cl.user_medias(user_id, amount=1)
        except Exception as e:
            print(f"⚠️ @{username} medya verisi alınamadı")
            return False

        if not medias:
            print(f"⚠️ @{username} için gönderi bulunamadı")
            return False
        
        # Yorum at
        try:
            media_id = medias[0].id
            comment = get_random_comment()
            cl.media_comment(media_id, comment)
            print(f"💬 @{username} gönderisine yorum: {comment}")
            
            # Medya objesini sil
            del medias
            del media_id
            
            mem_after = get_memory_usage()
            print(f"📊 RAM: {mem_after:.1f}MB (Δ{mem_after-mem_before:+.1f}MB)")
            
            return True
        except Exception as e:
            print(f"⚠️ @{username} yorum atılamadı")
            return False
        
    except Exception as e:
        print(f"❌ @{username} genel hata")
        return False
    finally:
        # Her işlem sonrası bellek temizleme
        force_garbage_collection()

def run_comment_cycle(cl):
    """Tüm sayfalara yorum atma döngüsü - bellek optimizasyonu ile"""
    # Target userları karıştır
    shuffled_users = random.sample(target_users, len(target_users))
    
    print(f"🎯 Bu döngüde {len(shuffled_users)} sayfaya yorum atılacak...")
    print(f"🧠 Başlangıç RAM: {get_memory_usage():.1f}MB")
    
    successful_comments = 0
    
    for i, username in enumerate(shuffled_users):
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
    
    # Sadece bellek temizleme - logout yok
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

def run_comment_loop():
    """Ana döngü - 60-90 dakika aralarla tüm sayfalara yorum at + takipçi isteklerini kontrol et"""
    loop_count = 0
    cl = None
    
    # İlk giriş
    try:
        cl = safe_login()
    except Exception as e:
        print(f"❌ İlk giriş başarısız: {str(e)}")
        return

    # Takipçi istekleri bilgisini göster
    if ACCEPT_REQUESTS_ENABLED:
        next_target = get_next_target_time()
        if next_target:
            print(f"🕒 Takipçi istekleri {ACCEPT_REQUESTS_TIME} saatinde kabul edilecek")
            print(f"📅 Sonraki hedef: {next_target.strftime('%Y-%m-%d %H:%M:%S')}")
    
    while True:
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
        
        # Bekleme sırasında takipçi isteklerini kontrol et (daha az sıklıkla)
        sleep_intervals = 600  # 10 dakika aralıklar (daha az sıklıkla kontrol)
        remaining_time = main_delay
        
        while remaining_time > 0:
            sleep_time = min(sleep_intervals, remaining_time)
            time.sleep(sleep_time)
            remaining_time -= sleep_time
            
            # Her 10 dakikada bir takipçi isteklerini kontrol et (daha az sıklıkla)
            if remaining_time > 0:
                check_and_accept_requests(cl)
                
                # Takipçi kontrolü sonrası bellek temizleme
                if remaining_time > 300:  # 5 dakikadan fazla kaldıysa
                    force_garbage_collection()

# ▶️ BAŞLAT
if __name__ == "__main__":
    print("🤖 Instagram Comment Bot + Takipçi İstekleri - RAM Optimized")
    print("📋 Hedef sayfalar:")
    for i, user in enumerate(target_users, 1):
        print(f"   {i}. @{user}")
    
    print(f"\n🕒 Takipçi istekleri ayarları:")
    print(f"   ✅ Özellik: {'Aktif' if ACCEPT_REQUESTS_ENABLED else 'Pasif'}")
    print(f"   ⏰ Hedef saat: {ACCEPT_REQUESTS_TIME}")
    print()
    
    # Başlangıç sistem bilgileri
    try:
        print(f"🧠 Sistem RAM: {psutil.virtual_memory().percent}%")
        print(f"💾 Kullanılabilir RAM: {psutil.virtual_memory().available / 1024 / 1024:.0f}MB")
    except:
        print("⚠️ Sistem bilgileri alınamadı")
    
    try:
        run_comment_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
        print("🔄 5 dakika sonra yeniden başlatılıyor...")
        time.sleep(300)  # 5 dakika bekle
        try:
            run_comment_loop()
        except:
            print("❌ Yeniden başlatma başarısız!")