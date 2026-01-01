import sqlite3

DB_FILE = "traffic.db"

def init_db(reset=False):
    """
    Initialize the traffic database.
    If reset=True, drop the table first (clean DB).
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS traffic")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS traffic (
            ts TEXT,
            iface TEXT,
            rx REAL,
            tx REAL
        )
    """)

    conn.commit()
    conn.close()
