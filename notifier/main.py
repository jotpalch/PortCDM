import os
import time
import psycopg2
import requests
from datetime import datetime, timedelta
import json
from psycopg2.extras import RealDictCursor
from config import notification_mapping, INOUT_PILOTAGE_EVENTS

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
        host='db'
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    interval_ago = datetime.now() - timedelta(seconds=interval)
    
    cur.execute('''
        WITH ranked_events AS (
            SELECT 
                se.*,
                ROW_NUMBER() OVER (PARTITION BY se.ship_voyage_number, se.event_name ORDER BY se.event_time DESC) as rn
            FROM ship_events se
            WHERE se.event_name IN ('修改進港預報', '修改出港預報')
        ),
        latest_event AS (
            SELECT 
                se.*,
                ROW_NUMBER() OVER (PARTITION BY se.ship_voyage_number ORDER BY se.event_time DESC) as rn
            FROM ship_events se
        )
        SELECT 
            ss.ship_name,
            ss.ship_voyage_number,
            eta.event_content as eta,
            etd.event_content as etd,
            le.event_name as latest_event_name,
            le.event_time as latest_event_time,
            le.navigation_status as navigation_status,
            le.event_content as latest_event_content,
            le.event_source as latest_event_source,
            ss.updated_at
        FROM ship_status ss
        LEFT JOIN ranked_events eta ON ss.ship_voyage_number = eta.ship_voyage_number 
            AND eta.event_name = '修改進港預報' AND eta.rn = 1
        LEFT JOIN ranked_events etd ON ss.ship_voyage_number = etd.ship_voyage_number 
            AND etd.event_name = '修改出港預報' AND etd.rn = 1
        LEFT JOIN latest_event le ON ss.ship_voyage_number = le.ship_voyage_number AND le.rn = 1
        WHERE ss.updated_at >= %s
        ORDER BY ss.updated_at DESC
    ''', (interval_ago,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [process_row(row) for row in rows]

def process_row(row):
    return {
        '船名': row['ship_name'],
        '船編': row['ship_voyage_number'][:6],
        '航次': row['ship_voyage_number'][6:10],
        'ETA': convert_to_timestamp(row['eta']),
        'ETD': convert_to_timestamp(row['etd']),
        '最新消息': convert_inout_pilotage_event(row['latest_event_name'], row['navigation_status']),
        '事件時間': convert_to_timestamp(row['latest_event_content']),
        '事件來源': row['latest_event_source'],
        '更新時間': row['updated_at']
    }

def convert_to_timestamp(date_string):
    if not date_string:
        return None
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y%m%d%H%M"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return date_string

def convert_inout_pilotage_event(event_name, navigation_status):
    if event_name in INOUT_PILOTAGE_EVENTS:
        return event_name + f" ({navigation_status})"
    return event_name

def format_message(row):
    ship_name = row['船名']
    ship_id = row['船編']
    voyage_number = row['航次']
    eta = row['ETA'].strftime("%Y/%m/%d %H:%M:%S") if row['ETA'] else "N/A"
    etd = row['ETD'].strftime("%Y/%m/%d %H:%M:%S") if row['ETD'] else "N/A"
    latest_event = row['最新消息']
    event_time = row['事件時間'].strftime("%Y/%m/%d %H:%M:%S") if isinstance(row['事件時間'], datetime) else row['事件時間']
    event_source = row['事件來源']
    updated_at = (row['更新時間'] + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S") if row['更新時間'] else "N/A"

    message = f"""

船名: {ship_name}
船編: {ship_id}
航次: {voyage_number}
ETA: {eta}
ETD: {etd}

最新事件: {latest_event}
事件時間: {event_time}
事件來源: {event_source}

更新時間: 
{updated_at}"""
    return message

def main():    
    original_token = os.getenv('LINE_NOTIFY_TOKEN')
    interval_time = int(os.getenv('INTERVAL_TIME', 180))

    line_notify_tokens = {
        'Pilot': os.getenv('LINE_NOTIFY_TOKEN_PILOT'),
        'Unmooring': os.getenv('LINE_NOTIFY_TOKEN_UNMOORING'),
        'Tugboat': os.getenv('LINE_NOTIFY_TOKEN_TUGBOAT'),
        'ShippingAgent': os.getenv('LINE_NOTIFY_TOKEN_SHIPPINGAGENT'),
        'ShippingCompany': os.getenv('LINE_NOTIFY_TOKEN_SHIPPINGCOMPANY'),
        'LoadingUnloading': os.getenv('LINE_NOTIFY_TOKEN_LOADINGUNLOADING')
    }

    while True:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 查看資料庫有無更新')
        rows = get_recent_ship_statuses(interval_time+1)

        for row in rows:
            message = format_message(row)
            latest_event = row['最新消息']
            
            if latest_event in notification_mapping:
                stakeholders = notification_mapping[latest_event]
                for stakeholder in stakeholders:
                    if stakeholder not in line_notify_tokens:
                        continue

                    token = line_notify_tokens[stakeholder]
                    if not token:
                        print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 無法發送通知: {row["船名"]} to {stakeholder}, TOKEN 未設置')
                        continue

                    response = send_line_notify(message, token)
                    if response.status_code == 200:
                        print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 通知發送成功: {row["船名"]} to {stakeholder}')
                    else:
                        print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 通知發送失敗: {row["船名"]} to {stakeholder}, 狀態碼: {response.status_code}')
                
                # Send a copy to the original token
                if original_token:
                    stakeholders_list = "\n".join(stakeholders)
                    message = f"\n通知對象: \n{stakeholders_list}" + message
                    response = send_line_notify(message, original_token)
                    if response.status_code == 200:
                        print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 通知發送成功: {row["船名"]} - 事件: {latest_event}')
                    else:
                        print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 通知發送失敗: {row["船名"]} - 事件: {latest_event}, 狀態碼: {response.status_code}')
            else:
                print(f'{(datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")} 未知事件類型: {latest_event}, 船名: {row["船名"]}')
                # pass

        time.sleep(interval_time)

if __name__ == "__main__":
    main()