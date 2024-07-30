import os
import time
from utils.fetch import fetch_webpage
from utils.extract import extract_ship_data
from utils.save import save_to_csv, save_to_html, save_to_db
import pandas as pd
from datetime import datetime

def main(url: str, output_csv_path: str, output_html_path: str, ship_content_id_prefix: str, cols: list[str]) -> None:
    # Fetch the webpage
    html = fetch_webpage(url)
    save_to_html(html, output_html_path)

    # Extract the ship data
    result_df = pd.DataFrame(columns=cols)
    ship_id = 0
    while True:
        ids = [f"{ship_content_id_prefix}{ship_id}_{num}" for num in range(0, 14)]

        # Check if the ship content exists
        result, df = extract_ship_data(html, ids, cols)
        if result == False:
            break

        # Append the ship data to the dataframe
        result_df = pd.concat([result_df, df], ignore_index=True)

        # Move to the next ship
        ship_id += 1

    # Save the ship data to csv
    save_to_csv(result_df, output_csv_path)

    # Store the ship data in the database
    save_to_db(result_df)

if __name__ == '__main__':
    from config import url, output_html_path, output_csv_path, ship_content_id_prefix, cols

    interval_time = int(os.getenv('INTERVAL_TIME', 300))

    time.sleep(20)

    while True:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 爬取網站資料')

        main(url, output_csv_path, output_html_path, ship_content_id_prefix, cols)

        time.sleep(interval_time)
