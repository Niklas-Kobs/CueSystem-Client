import os
import sqlite3
import webbrowser
import webview
import requests
import jsonLib as jl
import time
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HTML_FILE = os.path.join(BASE_DIR, 'gui', 'index.html')
DB_PATH = os.path.join(BASE_DIR, 'queue.db')
Favicon_FILE = os.path.join(BASE_DIR, 'gui', 'assets', 'favicon.png')

jl.libconfig (check=True, autoLoad=False, autoCreate=True, set_reset=True)

API_IP = jl.get ("queue_URL")

API_update = API_IP + "/update"
API_Msg = API_IP + "/message"
API_alive = API_IP + "/alive"
API_execute =  API_IP +"/execute"


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

    def get_config(self):
        config = jl.getAll()
        return config

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
                    'duration': data['duration'],
                    'is_called': 0  
                }

                patients.insert(int(target_index), new_patient)

                conn.execute('DELETE FROM queue')
                
                conn.executemany('''
                    INSERT INTO queue (patient_id, name, room, infos, doctor, duration, is_called)
                    VALUES (:patient_id, :name, :room, :infos, :doctor, :duration, :is_called)
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
            with sqlite3.connect('queue.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC LIMIT 5')
                for patient in cursor.fetchall():
                    rows.append(dict(patient))

                WNR_1 = rows[0]['patient_id'] if len(rows) > 0 else "---"
                Room_1 = rows[0]['room'] if len(rows) > 0 else "---"
                Status_1 = rows[0]['is_called'] if len(rows) > 0 else "---"
                call_1 = rows[0]['is_called'] if len(rows) > 0 else None

                WNR_2 = rows[1]['patient_id'] if len(rows) > 1 else "---"
                Room_2 = rows[1]['room'] if len(rows) > 1 else "---"
                Status_2 = rows[1]['is_called'] if len(rows) > 1 else "---"
                call_2 = rows[1]['is_called'] if len(rows) > 1 else None

                WNR_3 = rows[2]['patient_id'] if len(rows) > 2 else "---"
                Room_3 = rows[2]['room'] if len(rows) > 2 else "---"
                Status_3 = rows[2]['is_called'] if len(rows) > 2 else "---"
                call_3 = rows[2]['is_called'] if len(rows) > 2 else None

                WNR_4 = rows[3]['patient_id'] if len(rows) > 3 else "---"
                Room_4 = rows[3]['room'] if len(rows) > 3 else "---"
                Status_4 = rows[3]['is_called'] if len(rows) > 3 else "---"
                call_4 = rows[3]['is_called'] if len(rows) > 3 else None

                WNR_5 = rows[4]['patient_id'] if len(rows) > 4    else "---"
                Room_5 = rows[4]['room'] if len(rows) > 4 else "---"
                Status_5 = rows[4]['is_called'] if len(rows) > 4 else "---"
                call_5 = rows[4]['is_called'] if len(rows) > 4 else None

                if Status_1 == 1:
                    Status_1 = "Aufgerufen"
                elif Status_1 == 0:
                    Status_1 = "Bitte warten"
                else:
                    Status_1 = "---"

                if Status_2 == 1:
                    Status_2 = "Aufgerufen"
                elif Status_2 == 0:
                    Status_2 = "Bitte warten"
                else:                    
                    Status_2 = "---"
                
                if Status_3 == 1:
                    Status_3 = "Aufgerufen"
                elif Status_3 == 0:
                    Status_3 = "Bitte warten"
                else:                    
                    Status_3 = "---"

                if Status_4 == 1:
                    Status_4 = "Aufgerufen"
                elif Status_4 == 0:
                    Status_4 = "Bitte warten"
                else:                    
                    Status_4 = "---"

                if Status_5 == 1:
                    Status_5 = "Aufgerufen"
                elif Status_5 == 0:
                    Status_5 = "Bitte warten"
                else:                    
                    Status_5 = "---"

                if call_1 == 1:
                    call_1 = True
                else:                   
                    call_1 = None

                if call_2 == 1:
                    call_2 = True
                else:                   
                    call_2 = None

                if call_3 == 1:
                    call_3 = True
                else:                   
                    call_3 = None

                if call_4 == 1:
                    call_4 = True
                else:                   
                    call_4 = None

                if call_5 == 1:
                    call_5 = True
                else:                   
                    call_5 = None

                payload = {

                        "WNR_1": WNR_1,
                        "Room_1": Room_1,
                        "Status_1": Status_1,
                        "call_1": call_1,

                        "WNR_2": WNR_2,
                        "Room_2": Room_2,
                        "Status_2": Status_2,
                        "call_2": call_2,

                        "WNR_3": WNR_3,
                        "Room_3": Room_3,
                        "Status_3": Status_3,
                        "call_3": call_3,

                        "WNR_4": WNR_4,
                        "Room_4": Room_4,
                        "Status_4": Status_4,
                        "call_4": call_4,

                        "WNR_5": WNR_5,
                        "Room_5": Room_5,
                        "Status_5": Status_5,
                        "call_5": call_5,

                        "call_6": None,
                        "POP_H": "---",
                        "POP_T": "---"
                }
            print("Daten erfolgreich aus der DB gelesen:", payload)
            
            try:
                response_update = requests.post(API_update, json=payload)
                print(response_update.json())
            except Exception as e:
                print(f"Fehler beim Senden der Anfrage: {e}")

            return True
        except Exception as e:
            print(f"Fehler beim Auslesen: {e}")
            return False
        
    def Call_6(self):
        try:
            payload = {"exe": 1}
            response_update = requests.post(API_execute, json=payload)
            print(response_update.json())
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Anfrage: {e}")
            return False
    
    def send_message(self, subject, message):
        try:
            if not subject or not message:
                print("Betreff und Nachricht dürfen nicht leer sein.")
                return False

            if subject == "remove":
                payload = {"call_6": None,"POP_H": "---", "POP_T": "---"}
            else:
                payload = {"call_6": True,"POP_H": subject, "POP_T": message}

            response = requests.post(API_Msg, json=payload)
            print(response.json())
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Nachricht: {e}")
            return False
    
    def move_to_end(self, index):
        try:
            if index is None:
                print("Fehler: Index ist None")
                return False
                
            index = int(index)

            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
                patients = [dict(row) for row in cursor.fetchall()]

                if 0 <= index < len(patients):
                    target_patient = patients.pop(index)
                    patients.append(target_patient)

                    conn.execute('DELETE FROM queue')
                    conn.executemany('''
                        INSERT INTO queue (patient_id, name, room, infos, doctor, duration, is_called)
                        VALUES (:patient_id, :name, :room, :infos, :doctor, :duration, :is_called)
                    ''', patients)
                    
                    conn.commit()
                    return True
                else:
                    print(f"Index {index} außerhalb der Reichweite (Länge: {len(patients)})")
                    return False
        except Exception as e:
            print(f"Fehler beim Verschieben ans Ende: {e}")
            return False
        
    def move_to_top(self, index):
        try:
            if index is None:
                return False
                
            index = int(index)

            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
                patients = [dict(row) for row in cursor.fetchall()]

                if 0 <= index < len(patients):
                    target_patient = patients.pop(index)
                    
                    patients.insert(0, target_patient)

                    conn.execute('DELETE FROM queue')
                    conn.executemany('''
                        INSERT INTO queue (patient_id, name, room, infos, doctor, duration, is_called)
                        VALUES (:patient_id, :name, :room, :infos, :doctor, :duration, :is_called)
                    ''', patients)
                    
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Fehler beim Verschieben nach oben: {e}")
            return False
        
    def alive(self):
        msg = {}
        try:
            response_update = requests.post(API_alive, json=msg)
            print(response_update.json())
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Anfrage: {e}")
            return False
    
    def update_ID_py(self, new_ID):
        jl.edit ("start_ID", new_ID)
        return True
    
    def check_data(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(DB_PATH) as conn:
                sql = "DELETE FROM queue WHERE date(timestamp) <= date(?)"
                cursor = conn.execute(sql, (yesterday,))
                conn.commit()
                print(f"Erfolgreich gelöscht: {cursor.rowcount} Einträge vom {yesterday} und davor.")
                if cursor.rowcount == 0:
                    return 0
                else:
                    return 1
        except sqlite3.Error as e:
            print(f"Fehler beim Löschen: {e}")
            return 2
    
    def update_msg(self,msg_data):
        try:
            jl.edit("title",msg_data["msg_1_title"], group="msg_1")
            jl.edit("headline",msg_data["msg_1_headline"], group="msg_1")
            jl.edit("msg",msg_data["msg_1_msg"], group="msg_1")

            jl.edit("title",msg_data["msg_2_title"], group="msg_2")
            jl.edit("headline",msg_data["msg_2_headline"], group="msg_2")
            jl.edit("msg",msg_data["msg_2_msg"], group="msg_2")

            jl.edit("title",msg_data["msg_3_title"], group="msg_3")
            jl.edit("headline",msg_data["msg_3_headline"], group="msg_3")
            jl.edit("msg",msg_data["msg_3_msg"], group="msg_3")

            jl.edit("title",msg_data["msg_4_title"], group="msg_4")
            jl.edit("headline",msg_data["msg_4_headline"], group="msg_4")
            jl.edit("msg",msg_data["msg_4_msg"], group="msg_4")
            return True
        
        except Exception as e:
            print (e)
            return False
    
    def update_doc(self,doc_data):
        try:
            print (doc_data)
            jl.edit("name_1",doc_data["name_1"], group="doctor")
            jl.edit("name_2",doc_data["name_2"], group="doctor")
            jl.edit("name_3",doc_data["name_3"], group="doctor")
            jl.edit("name_4",doc_data["name_4"], group="doctor")
            jl.edit("name_5",doc_data["name_5"], group="doctor")
            jl.edit("name_6",doc_data["name_6"], group="doctor")
            return True
        
        except Exception as e:
            print (e)
            return False
        
    def update_url(self,url_data):
        try:
            print (url_data)
            jl.edit("queue_URL",url_data["queue_URL"])
            return True
        
        except Exception as e:
            print (e)
            return False

    
def main():
    api = WartelisteAPI()
    window = webview.create_window(
        title='Quesystem v2.0',
        url=HTML_FILE,
        js_api=api,
        width=1080,
        height=720,
        resizable=True
        )
    
    webview.start(lambda w: w.maximize(), window, icon=Favicon_FILE, debug=True)

if __name__ == '__main__':
    main()