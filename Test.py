import time
import requests

API_update = "http://192.168.0.200:50000/update"

Cue_Pos = 0

payload = {
    "PNr": PNr,
    "Cue_Pos": Cue_Pos,
    "Call": True,
    "delete": False,
    "Time": timestemp,
    "Timecode": timecode,
    "Posttime": Posttime,
    "Move": 234
}
try:
    response = requests.post(API_update, json=payload)
    Cue_Pos += 50
    print(response.json())
except Exception as e:
    print(f"Fehler beim Senden der Anfrage: {e}")
