import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta

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

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='db'
    )

def save_to_db(df: pd.DataFrame, table_name: str) -> None:
    save_functions = {
        'ship_status': save_ship_status_to_db,
        'ship_berth_order': save_ship_berth_order_to_db,
        'ship_voyage': save_ship_pass_time_to_db,
        'ship_events': save_ship_events_to_db
    }
    save_function = save_functions.get(table_name)
    if save_function:
        save_function(df)
    else:
        raise ValueError(f"Unsupported table name: {table_name}")

def save_ship_status_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_status (ship_voyage_number, ship_name, latest_event)
        VALUES (%s, %s, %s)
        ON CONFLICT (ship_voyage_number) DO UPDATE SET
            ship_name = EXCLUDED.ship_name,
            latest_event = EXCLUDED.latest_event,
            updated_at = CURRENT_TIMESTAMP
        WHERE EXCLUDED.latest_event != ship_status.latest_event
    '''
    data = [(row['船編航次'], row['船名'], row['最新事件']) for _, row in df.iterrows()]
    execute_batch_query(query, data)

def save_ship_berth_order_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_berth_order (
            berth_number, berthing_time, ship_status, pilotage_time,
            ship_name_chinese, ship_name_english, port_agent
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (berth_number, ship_name_chinese, ship_status) DO UPDATE SET
            berthing_time = EXCLUDED.berthing_time,
            pilotage_time = EXCLUDED.pilotage_time,
            ship_name_english = EXCLUDED.ship_name_english,
            port_agent = EXCLUDED.port_agent,
            updated_at = CURRENT_TIMESTAMP
        WHERE EXCLUDED.berthing_time != ship_berth_order.berthing_time
        OR EXCLUDED.pilotage_time != ship_berth_order.pilotage_time
        OR EXCLUDED.ship_name_english != ship_berth_order.ship_name_english
        OR EXCLUDED.port_agent != ship_berth_order.port_agent
    '''

    data = [(row['船席'], 
             convert_time(row['靠泊時間']),
             row['動態'], 
             convert_time(row['引水時間']),
             row['中文船名'], 
             row['英文船名'], 
             row['港代理']) for _, row in df.iterrows()]
    
    execute_batch_query(query, data)

def save_ship_pass_time_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_voyage (ship_voyage_number, pass_10_miles_time, pass_5_miles_time)
        VALUES (%s, %s, %s)
        ON CONFLICT (ship_voyage_number) DO UPDATE
        SET pass_10_miles_time = COALESCE(EXCLUDED.pass_10_miles_time, ship_voyage.pass_10_miles_time),
            pass_5_miles_time = COALESCE(EXCLUDED.pass_5_miles_time, ship_voyage.pass_5_miles_time),
            updated_at = CURRENT_TIMESTAMP
        WHERE 
            (EXCLUDED.pass_10_miles_time IS DISTINCT FROM ship_voyage.pass_10_miles_time)
            OR (EXCLUDED.pass_5_miles_time IS DISTINCT FROM ship_voyage.pass_5_miles_time)
    '''

    data = [(row['船編航次'], 
             convert_time(row['10浬']), 
             convert_time(row['5浬'])) 
            for _, row in df.iterrows()]
    execute_batch_query(query, data)

def convert_time(time_str):
    if time_str in ['待接靠', 'null', '', None]:
        return None
    if '/' in time_str:
        date_part, time_part = time_str.split(' ')
        year, month, day = map(int, date_part.split('/'))
        western_year = year + 1911
        if len(time_part.split(':')) == 2:
            time_part += ':00'
        dt = datetime.strptime(f"{western_year:04d}-{month:02d}-{day:02d} {time_part}", "%Y-%m-%d %H:%M:%S")
        utc_time = dt - timedelta(hours=8)
        return utc_time.strftime("%Y-%m-%d %H:%M:%S")
    return time_str

def save_ship_events_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_events (
            ship_voyage_number, event_source, event_time, event_name, 
            navigation_status, pilot_order_number, berth_number, event_content_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ship_voyage_number, event_time, event_name) DO UPDATE SET
            event_source = EXCLUDED.event_source,
            navigation_status = EXCLUDED.navigation_status,
            pilot_order_number = EXCLUDED.pilot_order_number,
            berth_number = EXCLUDED.berth_number,
            event_content_time = EXCLUDED.event_content_time
        WHERE (EXCLUDED.event_content_time IS DISTINCT FROM ship_events.event_content_time)
            OR (EXCLUDED.event_content_time IS NULL AND ship_events.event_content_time IS NOT NULL)
            OR (EXCLUDED.event_content_time IS NOT NULL AND ship_events.event_content_time IS NULL)
    '''
    
    def process_row(row):
        event_time = convert_to_24h_timestamp(row['發生時間'])
        event_content_time = convert_to_timestamp(row['事件內容'])
        return (
            row['船編航次'],
            row['事件來源'],
            (datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            row['事件名稱'],
            row['航行狀態'],
            row['引水單序號'],
            row['碼頭代碼'],
            (datetime.strptime(event_content_time, "%Y-%m-%d %H:%M:%S") - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S") if event_content_time else None
        )

    data = [process_row(row) for _, row in df.iterrows()]
    execute_batch_query(query, data)

def convert_to_24h_timestamp(time_str):
    date, time = time_str.split(' ', 1)
    period, time = time.rsplit(' ', 1)
    dt = datetime.strptime(f"{date} {time}", "%Y/%m/%d %I:%M:%S")
    if period == '下午' and dt.hour != 12:
        dt = dt.replace(hour=dt.hour + 12)
    elif period == '上午' and dt.hour == 12:
        dt = dt.replace(hour=0)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def convert_to_timestamp(time_str):
    if not time_str or time_str == 'null':
        return None
    
    try:
        if '/' in time_str:
            date, time = time_str.split()
            year, month, day = map(int, date.split('/'))
            western_year = year + 1911
            if len(time.split(':')) == 2:
                time += ':00'
            return f"{western_year:04d}-{month:02d}-{day:02d} {time}"
        elif len(time_str) == 12:
            return f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[8:10]}:{time_str[10:12]}:00"
        return None
    except:
        return None

def execute_batch_query(query: str, data: list) -> None:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(cur, query, data)
        conn.commit()