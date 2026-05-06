import sqlite3
import numpy as np
import pickle
import os

class FaceDatabase:
    def __init__(self, db_path='data/embeddings.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    last_name TEXT,
                    birthday TEXT,
                    nfc_uid TEXT UNIQUE,
                    encoding BLOB NOT NULL,
                    entry_time TEXT,
                    department TEXT,
                    position TEXT,
                    role TEXT,
                    registration_time TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT NOT NULL,
                    entry_time TEXT NOT NULL
                )
            ''')
            # Ensure removal_history is also updated

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS removal_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    last_name TEXT,
                    role TEXT,
                    position TEXT,
                    department TEXT,
                    birthday TEXT,
                    registration_time TEXT,
                    removal_time TEXT NOT NULL
                )
            ''')
            
            # Migrate removal_history if needed
            try:
                cursor.execute('ALTER TABLE removal_history ADD COLUMN position TEXT')
            except:
                pass
            try:
                cursor.execute('ALTER TABLE removal_history ADD COLUMN department TEXT')
            except:
                pass
            try:
                cursor.execute('ALTER TABLE removal_history ADD COLUMN birthday TEXT')
            except:
                pass
            
            # Ensure NFC UID is unique
            try:
                cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_nfc_uid ON persons(nfc_uid) WHERE nfc_uid IS NOT NULL AND nfc_uid != ""')
            except:
                pass
                
            conn.commit()

    def add_person(self, name, encoding, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            encoding_blob = pickle.dumps(encoding)
            cursor.execute('''
                INSERT INTO persons (name, last_name, birthday, nfc_uid, encoding, entry_time, role, position, department, registration_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, data.get('last_name', ''), data.get('birthday', ''), data.get('nfc_uid', ''), encoding_blob, data.get('entry_time', ''), data.get('role', ''), data.get('position', ''), data.get('department', ''), data.get('entry_time', '')))
            conn.commit()

    def update_person(self, original_name, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE persons
                SET name = ?, last_name = ?, birthday = ?, nfc_uid = ?, role = ?, position = ?, department = ?
                WHERE name = ?
            ''', (data.get('name'), data.get('last_name', ''), data.get('birthday', ''), data.get('nfc_uid', ''), data.get('role', ''), data.get('position', ''), data.get('department', ''), original_name))
            
            # Also update history table to reflect new name
            if data.get('name') != original_name:
                cursor.execute('UPDATE history SET person_name = ? WHERE person_name = ?', (data.get('name'), original_name))
            
            conn.commit()

    def log_entry(self, name, timestamp):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO history (person_name, entry_time) VALUES (?, ?)', (name, timestamp))
            # Also update last seen in persons table
            cursor.execute('UPDATE persons SET entry_time = ? WHERE name = ?', (timestamp, name))
            conn.commit()

    def get_person_history(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT entry_time FROM history WHERE person_name = ? ORDER BY entry_time DESC', (name,))
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def get_all_embeddings(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, encoding FROM persons')
            rows = cursor.fetchall()
            return [(row[0], pickle.loads(row[1])) for row in rows]

    def get_person_details(self, name):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM persons WHERE name = ?', (name,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_persons(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM persons ORDER BY registration_time DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_person_by_nfc(self, uid):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM persons WHERE nfc_uid = ?', (uid,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_person(self, name):
        from datetime import datetime
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch details before deleting to archive in removal_history
            cursor.execute('SELECT * FROM persons WHERE name = ?', (name,))
            person_row = cursor.fetchone()
            
            if person_row:
                p = dict(person_row)
                cursor.execute('''
                    INSERT INTO removal_history (name, last_name, role, position, department, birthday, registration_time, removal_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    p.get('name'), 
                    str(p.get('last_name') or ''), 
                    str(p.get('role') or ''), 
                    str(p.get('position') or ''), 
                    str(p.get('department') or ''), 
                    str(p.get('birthday') or ''),
                    str(p.get('registration_time') or ''),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            
            cursor.execute('DELETE FROM persons WHERE name = ?', (name,))
            # We preserve 'history' records for archival auditing 
            # until the admin explicitly deletes them.
            conn.commit()
            return cursor.rowcount > 0

    def permanently_delete_removed_person(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 1. Remove from removal_history
            cursor.execute('DELETE FROM removal_history WHERE name = ?', (name,))
            # 2. Remove all access logs
            cursor.execute('DELETE FROM history WHERE person_name = ?', (name,))
            conn.commit()
            return cursor.rowcount > 0

    def get_removal_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM removal_history ORDER BY removal_time DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def match_person(self, encoding, tolerance=0.6):
        import face_recognition
        # Setting image_label.setStyleSheet(f"border-radius: 20px;") is handled in GUI initialization to avoid per-frame lag
        all_embeddings = self.get_all_embeddings()
        if not all_embeddings:
            return None
        
        all_names, all_encodings = zip(*all_embeddings)
        distances = face_recognition.face_distance(all_encodings, encoding)
        min_dist_idx = np.argmin(distances)
        min_dist = distances[min_dist_idx]
        
        if min_dist <= tolerance:
            return all_names[min_dist_idx]
        return None

    def get_registration_stats(self):
        from datetime import datetime, timedelta
        stats = {
            "total": 0,
            "this_week": 0,
            "this_month": 0,
            "total_deleted": 0
        }
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT registration_time FROM persons')
            rows = cursor.fetchall()
            
            now = datetime.now()
            for row in rows:
                stats["total"] += 1
                reg_time_str = row[0]
                if reg_time_str:
                    try:
                        reg_date = datetime.strptime(reg_time_str, "%Y-%m-%d %H:%M:%S")
                        if now - reg_date <= timedelta(days=7):
                            stats["this_week"] += 1
                        if now.year == reg_date.year and now.month == reg_date.month:
                            stats["this_month"] += 1
                    except ValueError:
                        pass
            
            # Get deleted count
            cursor.execute('SELECT COUNT(*) FROM removal_history')
            stats["total_deleted"] = cursor.fetchone()[0]

        return stats
