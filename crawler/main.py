from utils.fetch import fetch_webpage
from utils.extract import extract_ship_data
from utils.save import save_to_csv, save_to_html
import pandas as pd

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

if __name__ == '__main__':
    from config import url, output_html_path, output_csv_path, ship_content_id_prefix, cols
    main(url, output_csv_path, output_html_path, ship_content_id_prefix, cols)
