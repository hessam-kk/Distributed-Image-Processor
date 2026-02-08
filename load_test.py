import requests
import concurrent.futures
import time

URL = "http://192.168.58.2:30005/upload"
FILE_PATH = "test.jpg"  # Ensure this file exists
TOTAL_REQUESTS = 20

def send_request(i):
    try:
        with open(FILE_PATH, 'rb') as f:
            files = {'file': f}
            data = {'effects': 'blur'} # Only target the slow service

            headers = {'Connection': 'close'}
            resp = requests.post(URL, files=files, data=data, headers=headers)

            return resp.status_code
    except Exception as e:
        return str(e)

print(f"--- Starting Load Test: {TOTAL_REQUESTS} concurrent requests ---")
print(f"--- Target: {URL} ---")
start_time = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=TOTAL_REQUESTS) as executor:
    results = list(executor.map(send_request, range(TOTAL_REQUESTS)))

duration = time.time() - start_time
print(f"--- Finished in {duration:.2f} seconds ---")