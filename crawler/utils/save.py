import os
import pandas as pd

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """
    Saves the given DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        output_path (str): The path where the CSV file will be saved.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

def save_to_html(html: str, output_path: str) -> None:
    """
    Saves the given HTML content to a file.

    Args:
        html (str): The HTML content to save.
        output_path (str): The path where the HTML file will be saved.
    """
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(html)
