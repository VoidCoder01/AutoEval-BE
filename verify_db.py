import sqlite3
import os

db_path = 'instance/evalai_new.db'

if os.path.exists(db_path):
    print(f"✅ Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check evaluations table schema
    cursor.execute('PRAGMA table_info(evaluations)')
    columns = cursor.fetchall()
    
    print(f"\n📊 Evaluations table has {len(columns)} columns:")
    for row in columns:
        print(f"  ✓ {row[1]} ({row[2]})")
    
    # Check if productivity_score exists
    column_names = [row[1] for row in columns]
    if 'productivity_score' in column_names:
        print(f"\n🎉 SUCCESS: productivity_score column found!")
    else:
        print(f"\n❌ ERROR: productivity_score column missing!")
    
    conn.close()
else:
    print(f"❌ Database not found: {db_path}")
