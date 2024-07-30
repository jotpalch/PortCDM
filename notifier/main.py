import os
import time
import psycopg2
import requests
from datetime import datetime, timedelta

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response

def get_recent_ship_statuses(interval):
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='db'  # Docker Compose 服務名稱
    )
    cur = conn.cursor()
    interval_ago = datetime.now() - timedelta(seconds=interval)
    cur.execute('''
        SELECT ship_voyage_number, ship_name, latest_event, port_entry_application,
               berth_shift_application, port_departure_application, offshore_vessel_entry,
               at_anchor, port_entry_in_progress, loading_unloading_notice,
               berth_shift_in_progress, berth_shift_loading_unloading,
               port_departure_in_progress, vessel_departed, created_at, updated_at
        FROM ship_status
        WHERE updated_at >= %s
    ''', (interval_ago,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def status_mapper(status):
    # Map the status values to symbols
    return {
        'YES': '✅',
        'NO': '',
        'RED': '🔴'
    }.get(status, status)  # Return the original status if it doesn't need to be mapped

def format_message(row):
    ship_voyage_number, ship_name, latest_event, port_entry_application, berth_shift_application, \
    port_departure_application, offshore_vessel_entry, at_anchor, port_entry_in_progress, \
    loading_unloading_notice, berth_shift_in_progress, berth_shift_loading_unloading, \
    port_departure_in_progress, vessel_departed, created_at, updated_at = row

    # Convert to UTC+8
    updated_at_utc8 = updated_at + timedelta(hours=8)
    # Format the datetime object back to string
    updated_at_str = updated_at_utc8.strftime("%Y-%m-%d %H:%M:%S")

    message = f"""

船舶航次號: {ship_voyage_number}
船名: {ship_name}
最新事件:  {latest_event}

進港申請:  {status_mapper(port_entry_application)}
移泊申請: {status_mapper(berth_shift_application)}
出港申請: {status_mapper(port_departure_application)}
離岸船舶進入: {status_mapper(offshore_vessel_entry)}
停錨: {status_mapper(at_anchor)}
進港進行中: {status_mapper(port_entry_in_progress)}
裝卸通知: {status_mapper(loading_unloading_notice)}
移泊進行中: {status_mapper(berth_shift_in_progress)}
移泊裝卸: {status_mapper(berth_shift_loading_unloading)}
出港進行中: {status_mapper(port_departure_in_progress)}
船舶離港: {status_mapper(vessel_departed)}

更新時間: 
{updated_at_str}"""
    return message

def main():
    # 從環境變數獲取 Line Notify 權杖
    line_notify_token = os.getenv('LINE_NOTIFY_TOKEN')

    interval_time = 60

    while True:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 查看資料庫有無更新')
        # 從資料庫獲取最近 interval_time 秒內的訊息
        rows = get_recent_ship_statuses(interval_time+1)

        for row in rows:
            message = format_message(row)
            response = send_line_notify(message, line_notify_token)
            if response.status_code == 200:
                print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 通知發送成功: {row[0]}')
            else:
                print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 通知發送失敗: {row[0]}, 狀態碼: {response.status_code}')

        # 等待 interval_time 秒
        time.sleep(interval_time)

if __name__ == "__main__":
    time.sleep(30)
    main()
