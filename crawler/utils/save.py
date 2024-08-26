import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

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
        WHERE (
            EXCLUDED.ship_name != ship_status.ship_name OR
            EXCLUDED.latest_event != ship_status.latest_event
        )
    '''
    data = [(row['船編航次'], row['船名'], row['最新事件']) for _, row in df.iterrows()]
    execute_batch_query(query, data)

def save_ship_berth_order_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_berth_order (
            berth_number, berthing_time, status, pilotage_time,
            ship_name_chinese, ship_name_english, port_agent
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (berth_number, ship_name_english) DO UPDATE SET
            berthing_time = EXCLUDED.berthing_time,
            status = EXCLUDED.status,
            pilotage_time = EXCLUDED.pilotage_time,
            ship_name_chinese = EXCLUDED.ship_name_chinese,
            port_agent = EXCLUDED.port_agent
        WHERE (
            EXCLUDED.berthing_time != ship_berth_order.berthing_time OR
            EXCLUDED.status != ship_berth_order.status OR
            EXCLUDED.pilotage_time != ship_berth_order.pilotage_time OR
            EXCLUDED.ship_name_chinese != ship_berth_order.ship_name_chinese OR
            EXCLUDED.port_agent != ship_berth_order.port_agent
        )
    '''
    data = [(row['船席'], row['靠泊時間'], row['動態'], row['引水時間'],
             row['中文船名'], row['英文船名'], row['港代理']) for _, row in df.iterrows()]
    execute_batch_query(query, data)

def save_ship_pass_time_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_voyage (ship_voyage_number, pass_10_miles_time, pass_5_miles_time)
        VALUES (%s, %s, %s)
        ON CONFLICT (ship_voyage_number) DO UPDATE
        SET pass_10_miles_time = CASE
                WHEN EXCLUDED.pass_10_miles_time IS NOT NULL THEN EXCLUDED.pass_10_miles_time
                ELSE ship_voyage.pass_10_miles_time
            END,
            pass_5_miles_time = CASE
                WHEN EXCLUDED.pass_5_miles_time IS NOT NULL THEN EXCLUDED.pass_5_miles_time
                ELSE ship_voyage.pass_5_miles_time
            END
    '''
    data = [(row['船編航次'], 
             row['10浬'] if row['10浬'] != 'null' else None, 
             row['5浬'] if row['5浬'] != 'null' else None) 
            for _, row in df.iterrows()]
    execute_batch_query(query, data)

def save_ship_events_to_db(df: pd.DataFrame) -> None:
    query = '''
        INSERT INTO ship_events (
            ship_voyage_number, event_source, event_time, event_name, 
            navigation_status, pilot_order_number, berth_code, event_content
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ship_voyage_number, event_time, event_name) DO UPDATE SET
            event_source = EXCLUDED.event_source,
            navigation_status = EXCLUDED.navigation_status,
            pilot_order_number = EXCLUDED.pilot_order_number,
            berth_code = EXCLUDED.berth_code,
            event_content = EXCLUDED.event_content
        WHERE (
            EXCLUDED.event_source != ship_events.event_source OR
            EXCLUDED.navigation_status != ship_events.navigation_status OR
            EXCLUDED.pilot_order_number != ship_events.pilot_order_number OR
            EXCLUDED.berth_code != ship_events.berth_code OR
            EXCLUDED.event_content != ship_events.event_content
        )
    '''
    def convert_to_24h_timestamp(time_str):
        date, time = time_str.split(' ', 1)
        period, time= time.rsplit(' ', 1)
        dt = datetime.strptime(f"{date} {time}", "%Y/%m/%d %I:%M:%S")
        if period == '下午' and dt.hour != 12:
            dt = dt.replace(hour=dt.hour + 12)
        elif period == '上午' and dt.hour == 12:
            dt = dt.replace(hour=0)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    data = [(row['船編航次'], row['事件來源'], convert_to_24h_timestamp(row['發生時間']), row['事件名稱'],
             row['航行狀態'], row['引水單序號'], row['碼頭代碼'], row['事件內容']) for _, row in df.iterrows()]
    execute_batch_query(query, data)

def execute_batch_query(query: str, data: list) -> None:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_batch(cur, query, data)
        conn.commit()