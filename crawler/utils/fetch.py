import requests
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
def fetch_webpage(url: str) -> str:
    """
    Fetches the content of a webpage.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        str: The HTML content of the webpage if the request is successful, None otherwise.
    """

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    driver = webdriver.Chrome()
    
    driver.get(url)#put here the adress of your page
    #elem = driver.find_elements_by_xpath("//*[@type='submit']")#put here the content you have put in Notepad, ie the XPath
    vessel = pd.DataFrame({"船編航次":[], "船名":[], "最新事件":[], "進港申請":[], "移泊申請":[], "出港申請":[], "港外船舶進港":[], "錨泊中":[], "進港作業中":[], "裝卸須知":[], "移泊作業中":[], "移泊裝卸作業":[], "出港作業中":[], "船舶已出港":[]})
    print(f"{vessel}")
    button = driver.find_element(By.ID, 'ASPx_船舶即時動態_DXPagerBottom_PBN') #Or find button by ID.
    check = True
    i = 0
    while check:
        list = []
        for j in range(0,14):
            try:   
                td = driver.find_element(By.ID, 'ASPx_船舶即時動態_tccell'+str(i)+'_'+str(j))
            except:
                check = False
                break
        # print(f"{td.text}")
            if j > 2:
                try:
                    text = td.find_element(By.XPATH, './/a//*').get_attribute("src")
                    if text == "https://sdci.kh.twport.com.tw/khbweb/images/ok.png":
                        list.append("true")
                    elif text == "https://sdci.kh.twport.com.tw/khbweb/images/red.gif":
                        list.append("RED")
                    else:
                        list.append("false")
                    continue
                    #print(f"{text}")
                except:
                    list.append("false")
                    #print(f"no")
                    continue
            text = td.text.replace("\n", " ")
            list.append(text)
        if not check:
            break
        listtodf=pd.DataFrame({"船編航次":[list[0]], "船名":[list[1]], "最新事件":[list[2]], "進港申請":[list[3]], "移泊申請":[list[4]], "出港申請":[list[5]], "港外船舶進港":[list[6]], "錨泊中":[list[7]], "進港作業中":[list[8]], "裝卸須知":[list[9]], "移泊作業中":[list[10]], "移泊裝卸作業":[list[11]], "出港作業中":[list[12]], "船舶已出港":[list[13]]})
        
        vessel = pd.concat([vessel, listtodf], ignore_index=True)
        print(f"{vessel}")
        if i%20 == 19:
            button.click()
            time.sleep(5)
            button = driver.find_element(By.ID, 'ASPx_船舶即時動態_DXPagerBottom_PBN')
        i = i+1
    vessel.to_csv('out.csv', index=False, encoding='utf_8_sig')
    time.sleep(5)
    driver.close()
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
    
    
