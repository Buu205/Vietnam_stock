
import requests
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_rubber_data_debug():
    url = "https://api2.simplize.vn/api/historical/prices/chart?ticker=TOCOM%3ATRB1!&period=all"
    
    # EXACT HEADERS FROM USER (minus variable token, plus cookies)
    # The user provided:
    # headers = {
    #   'accept': 'application/json, text/plain, */*',
    #   'accept-language': 'vi,en-US;q=0.9,en;q=0.8',
    #   'dnt': '1',
    #   'origin': 'https://simplize.vn',
    #   'priority': 'u=1, i',
    #   'referer': 'https://simplize.vn/',
    #   'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    #   'sec-ch-ua-mobile': '?0',
    #   'sec-ch-ua-platform': '"macOS"',
    #   'sec-fetch-dest': 'empty',
    #   'sec-fetch-mode': 'cors',
    #   'sec-fetch-site': 'same-site',
    #   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    #   'Cookie': 'JSESSIONID=cyYtXRLNvSsLfIzpIsjZ03B5GA90MQocYLeuJuyj'
    # }
    
    # I will use these exactly to verify.
    headers = {
      'accept': 'application/json, text/plain, */*',
      'accept-language': 'vi,en-US;q=0.9,en;q=0.8',
      'dnt': '1',
      'origin': 'https://simplize.vn',
      'priority': 'u=1, i',
      'referer': 'https://simplize.vn/',
      'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-site',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
      'Cookie': 'JSESSIONID=cyYtXRLNvSsLfIzpIsjZ03B5GA90MQocYLeuJuyj'
    }

    print(f"Testing URL: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Response: {resp.text}")
            return
            
        data = resp.json()
        points = data.get('data', [])
        print(f"Points found: {len(points)}")
        if points:
            print(f"Sample point: {points[0]}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    get_rubber_data_debug()
