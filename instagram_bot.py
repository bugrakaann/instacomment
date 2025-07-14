from instagrapi import Client
import random
import time
import itertools
from datetime import datetime

# ========== 🔐 Hesap Bilgileri ==========
USERNAME = "usr"       # Kendi kullanıcı adını yaz
PASSWORD = "pwd"        # Şifreni yaz

# ========== 🎯 Hedef Sayfalar ==========
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

# ========== ✨ Çeşitli Yorum Seçenekleri ==========
comments_pool = [
    # Emoji kombinasyonları
    "💅✨", "💄🌸", "💫🫦", "🪞🌟", "💁‍♀️🎀", "👠💅", "🌸💫", "💄🌟",
    "🫦💁‍♀️", "🎀👠", "💅🌸", "✨💄", "🌟🫦", "💁‍♀️🪞", "🎀💫",
    
    # Kısa kelimeler
    "güzel","merhaba", "harika","ankara", "süper", "👏", "🔥", "💖", "😍", "🥰", "❤️","slm", 
    "tatlı", "ciddi", "💕", "🌺", "✨", "💐", "🌹", "💜", "🧡",
    
    # Karma kombinasyonlar
    "çok güzel 💅", "harika 🌸", "süper ✨", "mükemmel 💫", "tatlı 🎀",
    "güzel paylaşım 💄", "beğendim 🌟", "çok tatlı 💁‍♀️", "harika 👠"
]

# ========== 🎲 Rastgele Yorum Seçimi ==========
def get_random_comment():
    return random.choice(comments_pool)

# ========== ⚙️ Instagram Giriş ==========
cl = Client()
cl.login(USERNAME, PASSWORD)
print(f"\n✅ Giriş başarılı @ {datetime.now().strftime('%H:%M:%S')}\n")

# ========== 🔁 Humanize Yorum Bot Döngüsü ==========
def run_comment_loop():
    loop_count = 0
    
    while True:
        loop_count += 1
        print(f"\n⏰ Döngü #{loop_count} başladı @ {datetime.now().strftime('%H:%M:%S')}")
        
        # Hedef kullanıcıları karıştır (her seferinde farklı sıra)
        shuffled_users = target_users.copy()
        random.shuffle(shuffled_users)
        
        for username in shuffled_users:
            try:
                # %25 ihtimal ile bu kullanıcıyı atla (daha human-like)
                if random.random() < 0.25:
                    print(f"⏭️ @{username} atlandı (rastgele skip)")
                    continue
                    
                user_id = cl.user_id_from_username(username)
                medias = cl.user_medias(user_id, amount=1)
                
                if not medias:
                    print(f"⚠️ @{username} için gönderi bulunamadı.")
                    continue
                    
                media = medias[0]
                media_id = media.id
                comment = get_random_comment()
                
                cl.media_comment(media_id, comment)
                print(f"💬 @{username} gönderisine yorum: {comment}")
                
            except Exception as e:
                print(f"❌ Hata @{username}: {str(e)}")
                # Hata durumunda biraz daha bekle
                time.sleep(random.randint(30, 60))

            # Sayfalar arası değişken bekleme (2-8 dakika)
            delay = random.randint(120, 480)
            print(f"⏳ Bekleme: {delay} saniye ({delay//60} dakika)...\n")
            time.sleep(delay)

        # Döngüler arası değişken bekleme (45 dakika - 3 saat)
        long_delay = random.randint(2700, 10800)  # 45dk - 3 saat
        hours = long_delay // 3600
        minutes = (long_delay % 3600) // 60
        
        print(f"🕒 Uzun uyku başlıyor @ {datetime.now().strftime('%H:%M:%S')}")
        print(f"⏰ Bekleme süresi: {hours} saat {minutes} dakika")
        
        # Her 10 döngüde bir 6-12 saat arası uzun mola
        if loop_count % 10 == 0:
            extra_delay = random.randint(21600, 43200)  # 6-12 saat
            total_delay = long_delay + extra_delay
            total_hours = total_delay // 3600
            print(f"😴 Uzun mola! Toplam bekleme: {total_hours} saat")
            time.sleep(total_delay)
        else:
            time.sleep(long_delay)

# ▶️ BOTU BAŞLAT
if __name__ == "__main__":
    print("🤖 Humanize Instagram Comment Bot v2.0")
    print("⚠️ Dikkat: Kendi sorumluluğunuzda kullanın!")
    print("🛑 Durdurmak için Ctrl+C basın\n")
    
    try:
        run_comment_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")