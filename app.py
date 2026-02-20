import os
import sqlite3
import webview

# Pfad-Konfiguration für die lokale HTML-Datei
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
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def get_queue(self):
        """Gibt die komplette Liste der Patienten-Objekte zurück."""
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row # Ermöglicht Zugriff über Spaltennamen
            cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
            # Wir wandeln die Zeilen in eine Liste von Dicts um für JS
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
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC')
            rows = cursor.fetchall()
            
            new_index = index - 1 if direction == 'up' else index + 1
            
            if 0 <= new_index < len(rows):
                # Die beiden betroffenen Zeilen als Dictionary holen
                row1 = dict(rows[index])
                row2 = dict(rows[new_index])
                
                # Die IDs behalten wir bei, aber wir tauschen alle anderen Inhalte
                # Wir updaten Zeile 1 mit den Werten von Zeile 2
                conn.execute('''
                    UPDATE queue 
                    SET patient_id=?, name=?, room=?, infos=?, doctor=?, duration=?
                    WHERE id=?''', 
                    (row2['patient_id'], row2['name'], row2['room'], row2['infos'], 
                    row2['doctor'], row2['duration'], row1['id']))
                
                # Wir updaten Zeile 2 mit den Werten von Zeile 1
                conn.execute('''
                    UPDATE queue 
                    SET patient_id=?, name=?, room=?, infos=?, doctor=?, duration=?
                    WHERE id=?''', 
                    (row1['patient_id'], row1['name'], row1['room'], row1['infos'], 
                    row1['doctor'], row1['duration'], row2['id']))
                
                conn.commit()
                return True
        return False

    def get_patient_details(self, index):
        """Holt die Details eines Patienten basierend auf dem Tabellen-Index aus der DB."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                # Wir nutzen LIMIT und OFFSET, um genau die Zeile zu finden, 
                # die im Frontend an Position 'index' steht.
                cursor = conn.execute('SELECT * FROM queue ORDER BY id ASC LIMIT 1 OFFSET ?', (index,))
                row = cursor.fetchone()
                if row:
                    return dict(row) # Wandelt die SQLite-Row in ein JS-taugliches Dict um
                return None
        except Exception as e:
            print(f"Datenbankfehler: {e}")
            return None

def main():
    api = WartelisteAPI()
    
    # Fenster erstellen - WICHTIG: Kein Webserver, lädt direkt die Datei
    window = webview.create_window(
        title='Quesystem v1.0',
        url=HTML_FILE,
        js_api=api,
        width=1080,
        height=720,
        resizable=True
        )

    # Startet die GUI
    webview.start(lambda w: w.maximize(), window)

if __name__ == '__main__':
    main()