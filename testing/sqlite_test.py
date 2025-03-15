import os
import sqlite3
import sys

# For files
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

# Replace 'your_database.db' with the actual path to the database file
db_path = "envHidden/data/WorktimeTrackerBak/WorktimeTracker.sqlite"

# Connect to the database
conn = sqlite3.connect(db_path)

# Create a cursor object
cursor = conn.cursor()

# Example: Fetch all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables:", tables)

# Close the connection when done
conn.close()