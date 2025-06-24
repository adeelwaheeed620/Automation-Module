import time
from pygologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Replace this with your real GoLogin API token
GOLOGIN_TOKEN = "your-gologin-api-token"

def create_and_launch_profile():
    gl = GoLogin({
        "token": GOLOGIN_TOKEN,
        "name": "New Login Profile",
        "os": "win"
    })
    profile_id = gl.create()
    profile_data = gl.start(profile_id)

    ws_url = profile_data["wsUrl"]
    hostport = ws_url.split("//")[1].split("/")[0]

    options = Options()
    options.debugger_address = hostport
    driver = webdriver.Chrome(options=options)

    # Replace this with the login or QR code page
    driver.get("https://example.com/login")

    print(f"[🟢] Please log in manually in the opened browser window.")
    print(f"[ℹ️] Profile ID: {profile_id}")
    print(f"[💾] Session will be auto-saved to this GoLogin profile.")

    # Keep the browser open for login
    while True:
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("[⛔] Exiting login setup.")
            break

    driver.quit()
    return profile_id

if __name__ == "__main__":
    pid = create_and_launch_profile()
    print(f"[✅] New Gologin Profile ID saved for automation: {pid}")
