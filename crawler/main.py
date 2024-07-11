import requests
from bs4 import BeautifulSoup
import pandas as pd

# Create output directory if not exists
url = 'https://sdci.kh.twport.com.tw/khbweb/UA1007.aspx'
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

# Check if the request is successful
if response.status_code == 200:

    # Save the webpage to output directory
    with open('output/output.html', 'w', encoding='utf-8') as file:
        file.write(response.text)

    # Parse the webpage
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define the ids and columns
    ids = [f"ASPx_船舶即時動態_tccell0_{num}" for num in range(0, 14)]
    cols = ["船編航次", "船名", "最新事件", "進港申請", "移泊申請", "出港申請", "港外船舶進港", "錨泊中", "進港作業中", "裝卸須知", "移泊作業中", "移泊裝卸作業", "出港作業中", "船舶已出港"]
    
    # Extract the data
    data = []
    for id in ids:
        # Find the content by id
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
            data.append("NO")

    df = pd.DataFrame([data], columns=cols)
    
    df.to_csv('output/output.csv', index=False)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
