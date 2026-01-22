import time
import requests

pi_url = "http://192.168.0.200:5000/update"

Cue_Pos = 0


while True:
    try:
        PNr = input("Bitte PNr eingeben: ")

        timestemp = time.time()

        timecode = time.strftime("%H:%M:%S")

        Posttime = timestemp


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
            response = requests.post(pi_url, json=payload)
            Cue_Pos += 50
            print(response.json())
        except Exception as e:
            print(f"Fehler beim Senden der Anfrage: {e}")
    except KeyboardInterrupt:
        print("Programm beendet.")
        break