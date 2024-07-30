CREATE TABLE IF NOT EXISTS ship_status (
    ship_voyage_number VARCHAR(10) PRIMARY KEY,
    ship_name VARCHAR(100),
    latest_event VARCHAR(100),
    port_entry_application VARCHAR(10),
    berth_shift_application VARCHAR(10),
    port_departure_application VARCHAR(10),
    offshore_vessel_entry VARCHAR(10),
    at_anchor VARCHAR(10),
    port_entry_in_progress VARCHAR(10),
    loading_unloading_notice VARCHAR(10),
    berth_shift_in_progress VARCHAR(10),
    berth_shift_loading_unloading VARCHAR(10),
    port_departure_in_progress VARCHAR(10),
    vessel_departed VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
CREATE TRIGGER update_timestamp_trigger
BEFORE UPDATE ON ship_status
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();