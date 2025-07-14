from instagrapi import Client
import random
import time
from datetime import datetime
import os

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

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

cl = Client()
cl.login(USERNAME, PASSWORD)
print(f"\n✅ Giriş başarılı @ {datetime.now().strftime('%H:%M:%S')}\n")

def comment_to_user(username):
    """Belirtilen kullanıcıya yorum at"""
    try:
        if random.random() < 0.1:  # %10 şansla skip (daha az skip)
            print(f"⏭️ @{username} atlandı (rastgele skip)")
            return False
        
        # Kullanıcı ID'sini al - sessizce hata yönet
        try:
            user_id = cl.user_id_from_username(username)
        except:
            print(f"⚠️ @{username} kullanıcısı bulunamadı")
            return False
        
        # Medyaları al - sessizce hata yönet
        try:
            medias = cl.user_medias(user_id, amount=1)
        except:
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
            return True
        except:
            print(f"⚠️ @{username} yorum atılamadı")
            return False
        
    except Exception as e:
        print(f"❌ @{username} genel hata")
        return False

def run_comment_cycle():
    """Tüm sayfalara yorum atma döngüsü"""
    # Target userları karıştır
    shuffled_users = random.sample(target_users, len(target_users))
    
    print(f"🎯 Bu döngüde {len(shuffled_users)} sayfaya yorum atılacak...")
    
    successful_comments = 0
    
    for i, username in enumerate(shuffled_users):
        print(f"\n📍 [{i+1}/{len(shuffled_users)}] @{username} işleniyor...")
        
        # Yorum at
        success = comment_to_user(username)
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
    
    print(f"\n📊 Döngü özeti: {successful_comments}/{len(shuffled_users)} başarılı yorum")
    return successful_comments

def run_comment_loop():
    """Ana döngü - 60-90 dakika aralarla tüm sayfalara yorum at"""
    loop_count = 0

    while True:
        loop_count += 1
        print(f"\n🔄 ===== DÖNGÜ #{loop_count} BAŞLIYOR ===== @ {datetime.now().strftime('%H:%M:%S')}")

        # Tüm sayfalara yorum at
        cycle_start = time.time()
        successful_comments = run_comment_cycle()
        cycle_end = time.time()
        
        cycle_duration = cycle_end - cycle_start
        print(f"\n✅ Döngü #{loop_count} tamamlandı!")
        print(f"📊 Başarılı yorum: {successful_comments}/{len(target_users)}")
        print(f"⏱️ Süre: {cycle_duration // 60:.0f} dakika {cycle_duration % 60:.0f} saniye")

        # Ana döngü bekleme süresi (60-90 dakika)
        main_delay = random.randint(3600, 5400)  # 60–90 dakika
        print(f"⏰ Sonraki döngüye kadar bekleme: {main_delay // 60} dakika")
        print(f"🕒 Sonraki döngü tahmini: {datetime.fromtimestamp(time.time() + main_delay).strftime('%H:%M:%S')}")
        print("=" * 50)
        
        time.sleep(main_delay)

# ▶️ BAŞLAT
if __name__ == "__main__":
    print("🤖 Instagram Comment Bot - Tüm Sayfalara Yorum (60–90dk döngü)")
    print("📋 Hedef sayfalar:")
    for i, user in enumerate(target_users, 1):
        print(f"   {i}. @{user}")
    print()
    
    try:
        run_comment_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
        print("🔄 Bot yeniden başlatılıyor...")
        time.sleep(60)  # 1 dakika bekle
        try:
            run_comment_loop()
        except:
            print("❌ Yeniden başlatma başarısız!")