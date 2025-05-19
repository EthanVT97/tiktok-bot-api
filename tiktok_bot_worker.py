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
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)

    try:
        # Start session and set cookie
        driver.get("https://www.tiktok.com")
        time.sleep(3)

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

        # Human-like scroll behavior
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(random.uniform(1.5, 2.5))

        follow_buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "Follow")]')
        followed_count = 0

        for btn in follow_buttons:
            if followed_count >= 5:
                break
            try:
                btn.click()
                time.sleep(random.uniform(2, 6))
                followed_count += 1

                # Try to extract username if available
                parent = btn.find_element(By.XPATH, './../..')
                username_elem = parent.find_element(By.XPATH, './/a[contains(@href, "/@")]')
                target_username = username_elem.get_attribute("href").split("/@")[-1] if username_elem else "unknown"

                print(f"[+] Followed: @{target_username}")

                # Supabase Logging
                try:
                    supabase.table("auto_follow").insert({
                        "user_id": user_id,
                        "target_username": target_username,
                        "timestamp": datetime.utcnow().isoformat(),
                        "action_type": "follow"
                    }).execute()
                except Exception as log_err:
                    print(f"[!] Logging failed: {log_err}")

            except Exception as e:
                print(f"[!] Error during follow: {str(e)}")
                continue

        print(f"[✓] Automation complete. Total followed: {followed_count}")

    except Exception as e:
        print(f"[✘] Fatal error occurred: {str(e)}")

    finally:
        driver.quit()
