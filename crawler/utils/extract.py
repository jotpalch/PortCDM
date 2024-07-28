from bs4 import BeautifulSoup
import pandas as pd
from typing import Tuple

def extract_ship_data(html: str, ids: list[str], cols: list[str]) -> Tuple[bool, pd.DataFrame]:
    """
    Extracts ship data from the given HTML content based on specified IDs.

    Args:
        html (str): The HTML content of the webpage.
        ids (List[str]): A list of HTML element IDs to find the ship data.
        cols (List[str]): A list of column names for the resulting DataFrame.

    Returns:
        Tuple[bool, pd.DataFrame]: A tuple where the first element is a boolean indicating
                                   whether the extraction was successful, and the second element
                                   is a DataFrame containing the extracted data.
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    for id in ids:
        content = soup.find(id=id)
        if content:
            cleaned_content = content.get_text(strip=True)
            img = content.find('img')
            if img and 'src' in img.attrs:
                img_src = img['src']
                if 'ok.png' in img_src:
                    cleaned_content += 'YES'
                elif 'red.gif' in img_src:
                    cleaned_content += 'RED'
            if cleaned_content == '':
                cleaned_content = 'NO'
            data.append(cleaned_content)
        else:
            return False, pd.DataFrame()
    return True, pd.DataFrame([data], columns=cols)
