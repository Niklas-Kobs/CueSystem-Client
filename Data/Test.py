import json
from cryptography.fernet import Fernet

# 1. Schlüssel generieren (Nur einmalig nötig, dann sicher speichern!)
key = Fernet.generate_key()
cipher_suite = Fernet(key)
print (f"Key {key}")
# Deine Daten
data = {
    "id": 42,
    "user": "Max Mustermann",
    "secret_info": "Geheime Botschaft"
}

# 2. JSON zu Bytes konvertieren
json_text = json.dumps(data).encode('utf-8')

# 3. Verschlüsseln
encrypted_text = cipher_suite.encrypt(json_text)
print(f"Verschlüsselt: {encrypted_text}")

# --- Und wieder zurück (Entschlüsseln) ---

# 4. Entschlüsseln
decrypted_text = cipher_suite.decrypt(encrypted_text)

# 5. Zurück zu JSON/Dict
original_data = json.loads(decrypted_text.decode('utf-8'))
print(f"Original: {original_data}")