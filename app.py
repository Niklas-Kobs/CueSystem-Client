import os
import sqlite3
import webbrowser
import webview

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'gui', 'index.html')
DB_PATH = os.path.join(BASE_DIR, 'warteliste.db')

class WartelisteAPI:
    def __init__(self):
        self._setup_db()
        

    def _setup_db(self):
        """Erstellt die erweiterte Tabelle für alle Patientendaten."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                name TEXT NOT NULL,
                room TEXT,
                infos TEXT,
                doctor TEXT,
                duration TEXT,
                is_called INTEGER DEFAULT 0, -- Hier direkt einfügen
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')

    def get_queue(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT id, patient_id, name, room, infos, doctor, duration, is_called FROM queue ORDER BY id ASC')
            return [dict(row) for row in cursor.fetchall()]

    def add_full_patient(self, data):
        """Erhält das Objekt von JS und speichert alle Felder."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                INSERT INTO queue (patient_id, name, room, infos, doctor, duration) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (data['id'], data['name'], data['room'], data['infos'], data['doctor'], data['duration']))
            return True

    def remove_entry(self, index):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute('SELECT id FROM queue ORDER BY id ASC LIMIT 1 OFFSET ?', (index,))
            row = cursor.fetchone()
            if row:
                conn.execute('DELETE FROM queue WHERE id = ?', (row[0],))
                return True
        return False

    def move_entry(self, index, direction):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
                patients = [dict(row) for row in cursor.fetchall()]

                new_index = index - 1 if direction == 'up' else index + 1

                if 0 <= new_index < len(patients):
                    
                    patients[index], patients[new_index] = patients[new_index], patients[index]

                    conn.execute('DELETE FROM queue')
                    conn.executemany('''
                        INSERT INTO queue (patient_id, name, room, infos, doctor, duration, is_called)
                        VALUES (:patient_id, :name, :room, :infos, :doctor, :duration, :is_called)
                    ''', patients)
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Fehler beim Verschieben: {e}")
        return False

    def get_patient_details(self, index):
        """Holt die Details eines Patienten basierend auf dem Tabellen-Index aus der DB."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC LIMIT 1 OFFSET ?', (index,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Datenbankfehler: {e}")
            return None
    
    def save_patient_edit(self, data):
        """Aktualisiert einen bestehenden Patienten in der Datenbank."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    UPDATE queue 
                    SET patient_id = ?, 
                        name = ?, 
                        room = ?, 
                        infos = ?, 
                        doctor = ?, 
                        duration = ?
                    WHERE id = ?
                ''', (data['patient_id'], data['name'], data['room'], 
                    data['infos'], data['doctor'], data['duration'], data['id']))
                conn.commit()
                return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    
    def add_at_position(self, data, target_index):
        """Fügt einen Patienten an einer bestimmten Position (0-basiert) ein."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
                patients = [dict(row) for row in cursor.fetchall()]

                new_patient = {
                    'patient_id': data['id'],
                    'name': data['name'],
                    'room': data['room'],
                    'infos': data['infos'],
                    'doctor': data['doctor'],
                    'duration': data['duration']
                }

                patients.insert(int(target_index), new_patient)

                conn.execute('DELETE FROM queue')
                conn.executemany('''
                    INSERT INTO queue (patient_id, name, room, infos, doctor, duration)
                    VALUES (:patient_id, :name, :room, :infos, :doctor, :duration)
                ''', patients)
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Fehler beim Einfügen an Position: {e}")
            return False
    
    def clear_all_entries(self):
        """Löscht alle Patienten aus der Datenbank."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('DELETE FROM queue')
                # Optional: Setzt auch den ID-Zähler (Autoincrement) zurück
                conn.execute('DELETE FROM sqlite_sequence WHERE name="queue"')
                conn.commit()
                return True
        except Exception as e:
            print(f"Fehler beim Leeren der DB: {e}")
            return False
        
    def toggle_call_status(self, index):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute('SELECT id, is_called FROM queue ORDER BY id ASC')
                rows = cursor.fetchall()
                target_id = rows[index][0]
                new_status = 1 if rows[index][1] == 0 else 0
                
                conn.execute('UPDATE queue SET is_called = ? WHERE id = ?', (new_status, target_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Fehler beim Call-Status: {e}")
            return False
    def open_external_link(self, url):
        webbrowser.open(url)
    
    def refresh(self):
        rows = []
        print("Refresh-Funktion aufgerufen")
        try:
            with sqlite3.connect('warteliste.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC LIMIT 5')
                for patient in cursor.fetchall():
                    rows.append(dict(patient))
                WNR_1 = rows[0]['name'] if len(rows) > 0 else "---"
                Timeestimate_1 = rows[0]['duration'] if len(rows) > 0 else "---"
                Status_1 = "Called" if rows[0]['is_called'] == 1 else "Waiting" if len(rows) > 0 else "---"
                call_1 = rows[0]['is_called'] == 1 if len(rows) > 0 else False
                WNR_2 = rows[1]['name'] if len(rows) > 1 else "---"
                Timeestimate_2 = rows[1]['duration'] if len(rows) > 1 else "---"
                Status_2 = "Called" if rows[1]['is_called'] == 1 else "Waiting" if len(rows) > 1 else "---"
                call_2 = rows[1]['is_called'] == 1 if len(rows) > 1 else False
                WNR_3 = rows[2]['name'] if len(rows) > 2 else "---"
                Timeestimate_3 = rows[2]['duration'] if len(rows) > 2 else "---"
                Status_3 = "Called" if rows[2]['is_called'] == 1 else "Waiting" if len(rows) > 2 else "---"
                call_3 = rows[2]['is_called'] == 1 if len(rows) > 2 else False
                WNR_4 = rows[3]['name'] if len(rows) > 3 else "---"
                Timeestimate_4 = rows[3]['duration'] if len(rows) > 3 else "---"
                Status_4 = "Called" if rows[3]['is_called'] == 1 else "Waiting" if len(rows) > 3 else "---"
                call_4 = rows[3]['is_called'] == 1 if len(rows) > 3 else False
                WNR_5 = rows[4]['name'] if len(rows) > 4    else "---"
                Timeestimate_5 = rows[4]['duration'] if len(rows) > 4 else "---"
                Status_5 = "Called" if rows[4]['is_called'] == 1 else "Waiting" if len(rows) > 4 else "---"
                call_5 = rows[4]['is_called'] == 1 if len(rows) > 4 else False
                payload = {

                        "WNR_1": WNR_1,
                        "Timeestimate_1": Timeestimate_1,
                        "Status_1": Status_1,
                        "call_1": call_1,

                        "WNR_2": WNR_2,
                        "Timeestimate_2": Timeestimate_2,
                        "Status_2": Status_2,
                        "call_2": call_2,

                        "WNR_3": WNR_3,
                        "Timeestimate_3": Timeestimate_3,
                        "Status_3": Status_3,
                        "call_3": call_3,

                        "WNR_4": WNR_4,
                        "Timeestimate_4": Timeestimate_4,
                        "Status_4": Status_4,
                        "call_4": call_4,

                        "WNR_5": WNR_5,
                        "Timeestimate_5": Timeestimate_5,
                        "Status_5": Status_5,
                        "call_5": call_5
                }
            print("Daten erfolgreich aus der DB gelesen:", payload)
            return True
        except Exception as e:
            print(f"Fehler beim Auslesen: {e}")
            return False

def main():
    api = WartelisteAPI()
    window = webview.create_window(
        title='Quesystem v1.0',
        url=HTML_FILE,
        js_api=api,
        width=1080,
        height=720,
        resizable=True
        )
    
    webview.start(lambda w: w.maximize(), window)

if __name__ == '__main__':
    main()