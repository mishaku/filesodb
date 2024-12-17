import sqlite3
import json

# Connect to SQLite database (or create it)
conn = sqlite3.connect('gids.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS gids (
    gid TEXT PRIMARY KEY,
    status BOOLEAN DEFAULT FALSE,
    error TEXT DEFAULT NULL,
    google JSON DEFAULT NULL
)
''')

# Read the gid.txt file
with open('gid.txt', 'r') as file:
    gids = file.readlines()

# Insert data into the table
for gid in gids:
    gid = gid.strip()
    cursor.execute('''
    INSERT OR IGNORE INTO gids (gid) VALUES (?)
    ''', (gid,))

# Commit and close
conn.commit()
conn.close()