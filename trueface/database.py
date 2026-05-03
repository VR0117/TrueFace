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
                    nfc_uid TEXT,
                    encoding BLOB NOT NULL,
                    entry_time TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT NOT NULL,
                    entry_time TEXT NOT NULL
                )
            ''')
            try:
                cursor.execute('ALTER TABLE persons ADD COLUMN role TEXT')
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def add_person(self, name, encoding, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            encoding_blob = pickle.dumps(encoding)
            cursor.execute('''
                INSERT INTO persons (name, last_name, birthday, nfc_uid, encoding, entry_time, role)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, data.get('last_name', ''), data.get('birthday', ''), data.get('nfc_uid', ''), encoding_blob, data.get('entry_time', ''), data.get('role', '')))
            conn.commit()

    def update_person(self, original_name, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE persons
                SET name = ?, last_name = ?, birthday = ?, nfc_uid = ?, role = ?
                WHERE name = ?
            ''', (data.get('name'), data.get('last_name', ''), data.get('birthday', ''), data.get('nfc_uid', ''), data.get('role', ''), original_name))
            
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
            cursor.execute('SELECT * FROM persons')
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
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM persons WHERE name = ?', (name,))
            conn.commit()
            return cursor.rowcount > 0

    def match_person(self, encoding, tolerance=0.6):
        import face_recognition
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
