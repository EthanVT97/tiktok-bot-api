import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from supabase import create_client, Client
import os

# -- Configurations --
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -- Core Automation --
def start_follow_bot(session_cookie: str, user_id: str, hashtag: str = "日本トレンド"):
    print("[+] Starting bot session...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    try:
        # Inject TikTok session cookie
        driver.get("https://www.tiktok.com")
        driver.add_cookie({
            'name': 'sessionid',
            'value': session_cookie,
            'domain': '.tiktok.com',
            'path': '/',
            'httpOnly': True,
            'secure': True
        })
        driver.get(f"https://www.tiktok.com/tag/{hashtag}")
        time.sleep(5)

        print("[+] Navigated to hashtag page")

        # Scroll to mimic human behavior
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(random.uniform(1, 2))

        follow_buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Follow")]')
        followed_count = 0

        for btn in follow_buttons:
            if followed_count >= 5:
                break
            try:
                btn.click()
                followed_count += 1
                print(f"[+] Followed user #{followed_count}")
                time.sleep(random.uniform(2, 6))

                # Log to Supabase
                supabase.table("auto_follow").insert({
                    "user_id": user_id,
                    "target_username": "unknown",  # (Optional: scrape username via DOM)
                    "timestamp": datetime.utcnow().isoformat(),
                    "action_type": "follow"
                }).execute()

            except Exception as e:
                print(f"[!] Follow failed: {str(e)}")
                continue

        print("[+] Automation complete")

    except Exception as e:
        print(f"[!] Fatal error: {str(e)}")

    finally:
        driver.quit()
