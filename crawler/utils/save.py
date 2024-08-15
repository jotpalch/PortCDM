import os
import pandas as pd
import psycopg2

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

def save_to_db(df: pd.DataFrame, table_name: str) -> None:
    if table_name == 'ship_status':
        save_ship_status_to_db(df)
    elif table_name == 'ship_berth_order':
        save_ship_berth_order_to_db(df)
    else:
        raise ValueError(f"Unsupported table name: {table_name}")

def save_ship_status_to_db(df: pd.DataFrame) -> None:
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='db'
    )
    cur = conn.cursor()
    
    for index, row in df.iterrows():
        cur.execute('''
            INSERT INTO ship_status (
                ship_voyage_number, ship_name, latest_event, port_entry_application,
                berth_shift_application, port_departure_application, offshore_vessel_entry,
                at_anchor, port_entry_in_progress, loading_unloading_notice,
                berth_shift_in_progress, berth_shift_loading_unloading,
                port_departure_in_progress, vessel_departed
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ship_voyage_number) DO UPDATE SET
                ship_name = EXCLUDED.ship_name,
                latest_event = EXCLUDED.latest_event,
                port_entry_application = EXCLUDED.port_entry_application,
                berth_shift_application = EXCLUDED.berth_shift_application,
                port_departure_application = EXCLUDED.port_departure_application,
                offshore_vessel_entry = EXCLUDED.offshore_vessel_entry,
                at_anchor = EXCLUDED.at_anchor,
                port_entry_in_progress = EXCLUDED.port_entry_in_progress,
                loading_unloading_notice = EXCLUDED.loading_unloading_notice,
                berth_shift_in_progress = EXCLUDED.berth_shift_in_progress,
                berth_shift_loading_unloading = EXCLUDED.berth_shift_loading_unloading,
                port_departure_in_progress = EXCLUDED.port_departure_in_progress,
                vessel_departed = EXCLUDED.vessel_departed
            WHERE (
                EXCLUDED.ship_name != ship_status.ship_name OR
                EXCLUDED.latest_event != ship_status.latest_event OR
                EXCLUDED.port_entry_application != ship_status.port_entry_application OR
                EXCLUDED.berth_shift_application != ship_status.berth_shift_application OR
                EXCLUDED.port_departure_application != ship_status.port_departure_application OR
                EXCLUDED.offshore_vessel_entry != ship_status.offshore_vessel_entry OR
                EXCLUDED.at_anchor != ship_status.at_anchor OR
                EXCLUDED.port_entry_in_progress != ship_status.port_entry_in_progress OR
                EXCLUDED.loading_unloading_notice != ship_status.loading_unloading_notice OR
                EXCLUDED.berth_shift_in_progress != ship_status.berth_shift_in_progress OR
                EXCLUDED.berth_shift_loading_unloading != ship_status.berth_shift_loading_unloading OR
                EXCLUDED.port_departure_in_progress != ship_status.port_departure_in_progress OR
                EXCLUDED.vessel_departed != ship_status.vessel_departed
            )
        ''', (
            row['船編航次'], row['船名'], row['最新事件'], row['進港申請'],
            row['移泊申請'], row['出港申請'], row['港外船舶進港'],
            row['錨泊中'], row['進港作業中'], row['裝卸須知'],
            row['移泊作業中'], row['移泊裝卸作業'],
            row['出港作業中'], row['船舶已出港']
        ))
    
    conn.commit()
    cur.close()
    conn.close()

def save_ship_berth_order_to_db(df: pd.DataFrame) -> None:
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='db'
    )
    cur = conn.cursor()
    
    for index, row in df.iterrows():
        cur.execute('''
            INSERT INTO ship_berth_order (
                berth_number, berthing_time, status, pilotage_time,
                ship_name_chinese, ship_name_english, port_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (berth_number, berthing_time) DO UPDATE SET
                status = EXCLUDED.status,
                pilotage_time = EXCLUDED.pilotage_time,
                ship_name_chinese = EXCLUDED.ship_name_chinese,
                ship_name_english = EXCLUDED.ship_name_english,
                port_agent = EXCLUDED.port_agent,
                updated_at = CURRENT_TIMESTAMP
            WHERE (
                EXCLUDED.status != ship_berth_order.status OR
                EXCLUDED.pilotage_time != ship_berth_order.pilotage_time OR
                EXCLUDED.ship_name_chinese != ship_berth_order.ship_name_chinese OR
                EXCLUDED.ship_name_english != ship_berth_order.ship_name_english OR
                EXCLUDED.port_agent != ship_berth_order.port_agent
            )
        ''', (
            row['泊位'], row['靠泊時間'], row['狀態'], row['引水時間'],
            row['船名(中文)'], row['船名(英文)'], row['港口代理']
        ))
    
    conn.commit()
    cur.close()
    conn.close()