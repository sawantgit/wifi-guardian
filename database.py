import sqlite3

DB_NAME = "database.db"

def init_db():
    """Creates the trusted devices table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trusted_devices (
            mac TEXT PRIMARY KEY,
            custom_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_trusted_device(mac, name):
    """Saves a device's MAC address as trusted."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO trusted_devices (mac, custom_name) VALUES (?, ?)", (mac.lower(), name))
    conn.commit()
    conn.close()

def remove_trusted_device(mac):
    """Removes a device from the trusted list."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trusted_devices WHERE mac = ?", (mac.lower(),))
    conn.commit()
    conn.close()

def get_all_trusted_macs():
    """Returns a dictionary of all trusted MAC addresses and their names."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT mac, custom_name FROM trusted_devices")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

# Initialize the database immediately when this module is referenced
init_db()
