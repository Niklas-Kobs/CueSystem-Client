import time
import requests

API_update = "http://192.168.0.200:50000/update"
API_alive = "http://192.168.0.200:50000/alive"
API_execute = "http://192.168.0.200:50000/execute"
API_call = "http://192.168.0.200:50000/call"


payload = {

        "WNR_1": "#0001",
        "Timeestimate_1": "12:00",
        "Status_1": "Waiting",
        "call_1": False,

        "WNR_2": "#0002",
        "Timeestimate_2": "12:30",
        "Status_2": "Waiting",
        "call_2": False,

        "WNR_3": "#0003",
        "Timeestimate_3": "13:00",
        "Status_3": "Waiting",
        "call_3": False,

        "WNR_4": "#0004",
        "Timeestimate_4": "13:30",
        "Status_4": "Waiting",
        "call_4": False,

        "WNR_5": "#0005",
        "Timeestimate_5": "---",
        "Status_5": "---",
        "call_5": False
}
try:
    response_update = requests.post(API_update, json=payload)
    print(response_update.json())
except Exception as e:
    print(f"Fehler beim Senden der Anfrage: {e}")

try:
    response_alive = requests.post(API_alive)
    print(response_alive.json())
except Exception as e:
    print(f"Fehler beim Senden der Anfrage: {e}")

try:
    execute = {"exe": "1"}
    response_exe = requests.post(API_execute,json=execute)
    print(response_exe.json())
except Exception as e:
    print(f"Fehler beim Senden der Anfrage: {e}")