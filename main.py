import os
import json
import requests
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse


# Rate limiter
MAX_REQUESTS = 10000
TIME_WINDOW = 10  # seconds
API_KEY = "AIzaSyAAhtyGtX-HMDcZHv22-9FoVmwliHidtDs"

def get_google_info(gid):
    # Simulate a request to Google API
    url = f"https://www.googleapis.com/books/v1/volumes/{gid}"
    # url = urllib.parse.quote(url)
    # print(url)
    # url2 = f'https://elitepressgmbh.com/filesoo/index.php?gmail=mitra1370v1370&url={url}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), 200
    else:
        return None, response.status_code

def main():
    output_file = 'explanations.json'
    explanations = {}
    max_workers = 1  # Adjust the number of workers based on your system's capability

    # Connect to SQLite database
    conn = sqlite3.connect('gids.db')
    cursor = conn.cursor()

    # Fetch GIDs with status False
    cursor.execute('SELECT gid FROM gids WHERE status = FALSE')
    gids = cursor.fetchall()

    request_count = 0
    start_time = time.time()

    for i, gid_tuple in enumerate(gids):
        gid = gid_tuple[0]
        
        # Rate limiting
        if request_count >= MAX_REQUESTS:
            elapsed_time = time.time() - start_time
            if elapsed_time < TIME_WINDOW:
                time.sleep(TIME_WINDOW - elapsed_time)
            start_time = time.time()
            request_count = 0

        google_info, error = get_google_info(gid)
        if google_info:
            cursor.execute('''
            UPDATE gids
            SET status = TRUE, google = ?, error = 200
            WHERE gid = ?
            ''', (json.dumps(google_info), gid))
        else:
            cursor.execute('''
            UPDATE gids
            SET error = ?
            WHERE gid = ?
            ''', (error, gid))
        
        request_count += 1
        print(i, f"{gid} {error}******" if error != 200 else "")
        if i % 100 == 0:
            print('commited')
            conn.commit()

    # Commit and close
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()