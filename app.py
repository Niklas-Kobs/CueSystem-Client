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
            cursor = conn.execute('SELECT id FROM queue ORDER BY id ASC')
            ids = [row[0] for row in cursor.fetchall()]
            
            new_index = index - 1 if direction == 'up' else index + 1
            if 0 <= new_index < len(ids):
                # Hier tauschen wir die kompletten Datensätze basierend auf den IDs
                id1, id2 = ids[index], ids[new_index]
                
                # Komplexer Tausch der Inhalte zweier Zeilen
                conn.execute('CREATE TEMPORARY TABLE temp_row AS SELECT * FROM queue WHERE id = ?', (id1,))
                conn.execute('UPDATE queue SET patient_id=(SELECT patient_id FROM queue WHERE id=?), name=(SELECT name FROM queue WHERE id=?), room=(SELECT room FROM queue WHERE id=?), doctor=(SELECT doctor FROM queue WHERE id=?) WHERE id=?', (id2, id2, id2, id2, id1))
                conn.execute('UPDATE queue SET patient_id=(SELECT patient_id FROM temp_row), name=(SELECT name FROM temp_row), room=(SELECT room FROM temp_row), doctor=(SELECT doctor FROM temp_row) WHERE id=?', (id2,))
                conn.execute('DROP TABLE temp_row')
                return True
        return False

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