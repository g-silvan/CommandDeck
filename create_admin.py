import mariadb as db
from dotenv import load_dotenv
import bcrypt
import os

load_dotenv()

# Database Config
db_user = os.getenv("DBUSER")
db_password = os.getenv("DBPASS")
db_host = os.getenv("DBHOST")
db_database = os.getenv("DBNAME")

def create_user(username, plain_password, permission_level):
    try:
        # Passwort hashen
        hashed_pw = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        
        conn = db.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_database
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password_hash, permission_level) VALUES (?, ?, ?)",
            (username, hashed_pw.decode('utf-8'), permission_level))
        
        conn.commit()
        print(f"Benutzer {username} erfolgreich angelegt!")
    except db.Error as e:
        if hasattr(e, 'errno') and e.errno == 1062:
            print(f"Fehler: Benutzername '{username}' existiert bereits.")
        else:
            print(f"Fehler: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()


create_user("admin", "commanddeck", "admin")

