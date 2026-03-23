import bcrypt
import jsonLib as j

password = j.get("M.Mustermann", group= "nutzer").encode('utf-8')

print (password)

# hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

# print(f"Dieser Wert kommt in die Datenbank: {hashed_password.decode('utf-8')}")


eingabe = input("INPUT:").encode('utf-8')

if bcrypt.checkpw(eingabe, password):
    print("Login erfolgreich!")
else:
    print("Passwort falsch!")