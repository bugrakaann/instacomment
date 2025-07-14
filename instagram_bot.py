from instagrapi import Client
import random
import time
from datetime import datetime
import itertools
import os

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

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
    "çok güzel 💅", "harika 🌸", "süper ✨", "mükemmel 💫", "tatlı 🎀",
    "güzel paylaşım 💄", "beğendim 🌟", "çok tatlı 💁‍♀️", "harika 👠"
]

def get_random_comment():
    return random.choice(comments_pool)

cl = Client()
cl.login(USERNAME, PASSWORD)
print(f"\n✅ Giriş başarılı @ {datetime.now().strftime('%H:%M:%S')}\n")

def run_comment_loop():
    loop_count = 0
    user_cycle = itertools.cycle(random.sample(target_users, len(target_users)))

    while True:
        loop_count += 1
        print(f"\n⏰ Döngü #{loop_count} @ {datetime.now().strftime('%H:%M:%S')}")

        username = next(user_cycle)

        try:
            if random.random() < 0.3:
                print(f"⏭️ @{username} atlandı (rastgele skip)")
            else:
                user_id = cl.user_id_from_username(username)
                try:
                    medias = cl.user_medias(user_id, amount=1)
                except KeyError:
                    print(f"⚠️ Instagram yanıtında 'data' eksik: @{username}")
                    continue

                if not medias:
                    print(f"⚠️ @{username} için gönderi bulunamadı.")
                else:
                    media_id = medias[0].id
                    comment = get_random_comment()
                    cl.media_comment(media_id, comment)
                    print(f"💬 @{username} gönderisine yorum: {comment}")

        except Exception as e:
            print(f"❌ Hata @{username}: {str(e)}")
            time.sleep(random.randint(30, 60))

        delay = random.randint(3600, 5400)  # 60–90 dakika
        print(f"⏳ Bekleme: {delay // 60} dakika...\n")
        time.sleep(delay)

# ▶️ BAŞLAT
if __name__ == "__main__":
    print("🤖 Instagram Comment Bot (60–90dk)")
    try:
        run_comment_loop()
    except KeyboardInterrupt:
        print("\n🛑 Bot durduruldu!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {str(e)}")
