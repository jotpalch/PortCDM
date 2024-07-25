import os
from typing import Tuple
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_webpage(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

    # Check if the request is successful
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

def extract_ship_data(html, ids, cols) -> Tuple[bool, pd.DataFrame]:
    # Parse the webpage
    soup = BeautifulSoup(html, 'html.parser')

    # Extract the ship data
    data = []
    for id in ids:
        # Find the ship content by html id
        content = soup.find(id=id)
        if content:
            # Clean the content
            cleaned_content = content.get_text(strip=True)

            # Check if the content contains image
            img = content.find('img')
            if img and 'src' in img.attrs:
                img_src = img['src']
                if 'ok.png' in img_src:
                    cleaned_content += 'YES'
                elif 'red.gif' in img_src:
                    cleaned_content += 'RED'

            # Check if the content is empty
            if cleaned_content == '':
                cleaned_content = 'NO'
            
            data.append(cleaned_content)
        else:
            return False, pd.DataFrame()
    
    return True, pd.DataFrame([data], columns=cols)

def save_to_csv(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

def save_to_html(html, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html)

def main(url, output_csv_path, output_html_path, ship_content_id_prefix, cols):
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
    # Define the variables
    url = 'https://sdci.kh.twport.com.tw/khbweb/UA1007.aspx'
    output_html_path = 'output/output.html'
    output_csv_path = 'output/output.csv'
    ship_content_id_prefix = 'ASPx_船舶即時動態_tccell'
    cols = ["船編航次", "船名", "最新事件", "進港申請", "移泊申請", "出港申請", "港外船舶進港", "錨泊中", "進港作業中", "裝卸須知", "移泊作業中", "移泊裝卸作業", "出港作業中", "船舶已出港"]

    # Run the main function
    main(url, output_csv_path, output_html_path, ship_content_id_prefix, cols)