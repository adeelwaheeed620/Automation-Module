import asyncio
import json
import time
import requests
import websockets
from pygologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

with open("config.json") as f:
    CONFIG = json.load(f)

GOLOGIN_TOKEN = CONFIG["api_token"]
WS_URL = CONFIG["websocket_url"]

class ProxyExpiredException(Exception): pass
class AccountExpiredException(Exception): pass
class LoginFailedException(Exception): pass

def start_gologin_profile(profile_id):
    try:
        gl = GoLogin({"token": GOLOGIN_TOKEN, "profile_id": profile_id})
        profile_data_raw = gl.start()
        profile_data = json.loads(profile_data_raw) if isinstance(profile_data_raw, str) else profile_data_raw
        ws_url = profile_data["wsUrl"]
        hostport = ws_url.split("//")[1].split("/")[0]
        options = Options()
        options.debugger_address = hostport
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        if "proxy" in str(e).lower():
            raise ProxyExpiredException("Proxy expired or invalid.")
        raise

def perform_task(driver, task):
    try:
        driver.get(task["url"])
    except WebDriverException as e:
        if "proxy" in str(e).lower():
            raise ProxyExpiredException()
        raise

    time.sleep(2)
    for step in task.get("actions", []):
        action = step["action"]
        selector = step["selector"]
        try:
            if action == "fill":
                el = driver.find_element(By.CSS_SELECTOR, selector)
                el.clear()
                el.send_keys(step["value"])
            elif action == "select":
                el = driver.find_element(By.CSS_SELECTOR, selector)
                for option in el.find_elements(By.TAG_NAME, 'option'):
                    if option.get_attribute("value") == step["value"]:
                        option.click()
                        break
            elif action == "click":
                driver.find_element(By.CSS_SELECTOR, selector).click()
            time.sleep(1)
        except NoSuchElementException:
            raise LoginFailedException(f"Element not found: {selector}")
        except Exception as e:
            raise Exception(f"DOM interaction failed: {e}")

    result = None
    try:
        if "result_selector" in task:
            el = driver.find_element(By.CSS_SELECTOR, task["result_selector"])
            if el.tag_name == "img":
                result = el.get_attribute("src")
            else:
                result = el.text.strip()
    except NoSuchElementException:
        result = "Result element not found"
    except Exception as e:
        result = f"Error extracting result: {e}"
    return result

def send_result(callback_url, payload):
    try:
        res = requests.post(callback_url, json=payload, timeout=10)
        print(f"[→] Sent result to backend ({res.status_code})")
    except Exception as e:
        print(f"[X] Failed to send result: {e}")

async def handle_message(task_json):
    print("[📥] Received task:", task_json.get("orderId", "unknown"))
    status = "PAYMENT_FAILED"
    message = ""
    result = None
    try:
        driver = start_gologin_profile(task_json["profile_id"])
        result = perform_task(driver, task_json)
        driver.quit()
        status = "PAYMENT_SUCCESS"
        message = "任务完成"
    except ProxyExpiredException:
        status = "PROXY_EXPIRED"
        message = "Proxy expired or unreachable"
    except AccountExpiredException:
        status = "ACCOUNT_EXPIRED"
        message = "Account session expired"
    except LoginFailedException as e:
        status = "LOGIN_FAILED"
        message = str(e)
    except Exception as e:
        status = "PAYMENT_FAILED"
        message = f"Automation failed: {e}"

    response_payload = {
        "orderId": task_json.get("orderId"),
        "success": status == "PAYMENT_SUCCESS",
        "message": message,
        "status": status,
        "details": {
            "success": status == "PAYMENT_SUCCESS",
            "duration": 5000,
            "timestamp": int(time.time() * 1000),
            "orderId": task_json.get("orderId"),
            "status": status,
            "paymentMethod": task_json.get("paymentMethod", "unknown"),
            "amount": task_json.get("amount", 1),
            "result": result
        }
    }

    if "callback_url" in task_json:
        send_result(task_json["callback_url"], response_payload)
    else:
        print("[i] No callback_url provided. Result not posted.")
        print(response_payload)

async def listen_forever():
    while True:
        try:
            print(f"[🔌] Connecting to {WS_URL}")
            async with websockets.connect(WS_URL) as ws:
                print("[🟢] Connected and listening for tasks...")
                async for message in ws:
                    try:
                        task_json = json.loads(message)
                        await handle_message(task_json)
                    except Exception as e:
                        print(f"[X] Error handling message: {e}")
        except Exception as conn_err:
            print(f"[X] Connection error: {conn_err}")
        print("[🔁] Reconnecting in 5 seconds...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen_forever())
