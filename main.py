import os # Betriebsystemfunktionen
import random # Zufallszahlen
import subprocess # Ausführen von Shell-Befehlen
import bcrypt # Passwort-Hashing
import mariadb as db #Datenbankverbindung
from dotenv import load_dotenv #U mgebungsvariablen
from flask_wtf.csrf import CSRFProtect
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user



# Lade die Umgebungsvariablen aus der .env Datei
load_dotenv(dotenv_path=".env")

db_user = os.getenv("DBUSER")
db_password = os.getenv("DBPASS")
db_host = os.getenv("DBHOST")
db_database = os.getenv("DBNAME")
web_port = os.getenv("WEBPORT")
timeout = int(os.getenv("timeout"))
sshkey_path = os.getenv("SSHKEY_PATH")
publicsshkey_path = os.getenv("PUBLICSSHKEY_PATH") 
SECRET_KEY = os.getenv("SECRET_KEY")
HTTPS_ONLY = os.getenv("HTTPS_ENABLED")

# Falls HTTPS_ONLY klein geschrieben ist, wird es in Großbuchstaben umgewandelt
if HTTPS_ONLY is not None:
    HTTPS_ONLY = HTTPS_ONLY.capitalize() == "True"

print(f"HTTPS_ONLY: {HTTPS_ONLY}")

publicsshkey_path = os.path.expanduser(publicsshkey_path) 

try:
    with open(publicsshkey_path, 'r') as file:
        publickey = file.read()
except Exception as e:
    print(f"Fehler beim Laden des Public SSH Keys: {e}")
    publickey = ""


# Verbindung zur Datenbank

def get_db_connection():
    try:
        connection = db.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_database)
        return connection
    except db.Error as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None

# Funktion um alle Buttons eines Benutzers abzufragen
def get_user_buttons(username):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # User-ID abfragen
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))

            user_row = cursor.fetchone() 
            user_id = user_row[0] # Erster Wert von der Ausgabe als user_id festlegen

            # Buttons abfragen
            cursor.execute("SELECT buttons.button_id, buttons.button_name, buttons.button_command, buttons.button_color, buttons.sort_order FROM buttons JOIN user_buttons ON buttons.button_id = user_buttons.button_id WHERE user_buttons.user_id = ? ORDER BY buttons.sort_order ASC", (user_id,))

            rows = cursor.fetchall() # Alle Zeilen abfragen
            conn.close # Verbindung zur Datenbank schließen

            buttons = [{'id': button_id, 'name': button_name, 'command': button_command, 'color': button_color, 'sort_order': sort_order}
                       for (button_id, button_name, button_command, button_color, sort_order) in rows] # Liste der Buttons erstellen
            return(buttons)
    # Fehlerbehandlung
    except db.Error as e:
        print(f"Fehler beim Laden der Buttons: {e}")
        return []
    

def  get_all_buttons():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT button_id, button_name, button_command, COALESCE(button_color, '#3498db') AS button_color, sort_order FROM buttons ORDER BY sort_order ASC")
            rows = cursor.fetchall()
            conn.close()
            buttons = [{'id': button_id, 'name': button_name, 'command': button_command, 'color': button_color, 'sort_order': sort_order}
                       for (button_id, button_name, button_command, button_color, sort_order) in rows]
            return buttons
    except db.Error as e:
        print(f"Fehler beim Laden aller Buttons: {e}")
        return []

            
    
# Funktion um den höchsten Sortierwert abzufragen
def get_max_sort_order():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(sort_order) FROM buttons")
            max_order = cursor.fetchone()[0]
            conn.close()
            return max_order if max_order is not None else 0
    except db.Error as e:
        print(f"Fehler beim Abrufen der maximalen Sortierreihenfolge: {e}")
        return 0

# Funktion um eine Button ID zu generieren

def generate_button_id():
    button_id = random.randint(1000, 9999)
    while not check_button_id_unique(button_id):
        generate_button_id()
    return button_id



# Funktion um zu prüfen ob die Button ID schon existiert
def check_button_id_unique(button_id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            statement = "SELECT COUNT(*) FROM buttons WHERE button_id = %s"
            data = (button_id,)
            cursor.execute(statement, data)
            (count,) = cursor.fetchone()
            conn.close()
            return count == 0
    except db.Error as e:
        print(f"Fehler beim Überprüfen der ButtonID: {e}")
        return False





# Funktion um neue  Buttons zu  erstellen
def create_button(button_name, button_command, button_color,  sort_order):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            if sort_order is None or sort_order == "":
                sort_order = get_max_sort_order() + 1  # Wenn kein Sortierwert angegeben ist, den aktuell höchsten Sortierwert + 1 verwenden
            else:
                sort_order = int(sort_order)
            
            # 4 Stellige Button ID generieren
            button_id =  generate_button_id()

            # Vorhandene Buttons mit höherem Sortierwert um 1 erhöhen
            cursor.execute("UPDATE buttons SET sort_order = sort_order + 1 WHERE sort_order >= %s", (sort_order,))

            # Neuen Button in die Datenbank einfügen
            statement = "INSERT INTO buttons (button_id, button_name, button_command, button_color, sort_order) VALUES (%s, %s, %s, %s, %s)"
            data = (button_id, button_name, button_command, button_color, sort_order)
            cursor.execute(statement, data)
            conn.commit()
            conn.close()
            
            return f"Button '{button_name}' auf Position {sort_order} hinzugefügt."

    # Fehlerbehandlung
    except db.Error as e:
        conn.rollback()
        conn.close()
        return f"Datenbankfehler: {e}"
    

# Funktion um einen Button zu löschen
def delete_button(button_name):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Prüfen ob der Button existiert
            statement_check = "SELECT COUNT(*) FROM buttons WHERE button_name = %s"
            data_check = (button_name,)
            cursor.execute(statement_check, data_check)
            (count,) = cursor.fetchone() 
            if count == 0: # Falls der Button nicht existiert
                conn.close()
                return f"Button '{button_name}' existiert nicht."
            else:
                # Sortierwert des Buttons abfragen
                cursor.execute("SELECT sort_order FROM buttons WHERE button_name = %s", (button_name,))
                (sort_order,) = cursor.fetchone()

                # Button löschen
                statement_delete = "DELETE FROM buttons WHERE button_name = %s"
                data_delete = (button_name,)
                cursor.execute(statement_delete, data_delete)

                # Sortierreihenfolge der verbleibenden Buttons anpassen
                cursor.execute("UPDATE buttons SET sort_order = sort_order - 1 WHERE sort_order > %s", (sort_order,))

                conn.commit()
                conn.close()
                return f"Button '{button_name}' erfolgreich gelöscht."
            
    # Fehlerbehandlung
    except db.Error as e:
        conn.rollback() # Rückgängig machen der Änderungen
        conn.close() # Verbindung schließen
        return f"Datenbankfehler: {e}"
 

def modify_button(button_id, new_name, new_command, new_color, new_sort_order):
    print(f"Modifying button with ID: {button_id}, new name: {new_name}, new command: {new_command}, new color: {new_color}, new sort order: {new_sort_order}")
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Konvertiere new_sort_order zu Integer
            new_sort_order = int(new_sort_order)

            # Wenn keine neue Farbe angegeben ist, die aktuelle Farbe aus der Datenbank abrufen
            if not new_color or new_color.strip() == "":
                cursor.execute("SELECT button_color FROM buttons WHERE button_id = %s", (button_id,))
                result = cursor.fetchone()
                if result:
                    new_color = result[0]  # Aktuelle Farbe aus der Datenbank übernehmen
                else:
                    new_color = "#3498db"  # Fallback auf Standardfarbe

            # Abfrage des aktuellen Sortierwerts
            cursor.execute("SELECT sort_order FROM buttons WHERE button_id = %s", (button_id,)) 
            old_sort_order = cursor.fetchone()[0]
            print(f"Old sort order: {old_sort_order}")
            print(f"New sort order: {new_sort_order}")
            max_sort_order = get_max_sort_order()

            if new_sort_order != old_sort_order:
                print("1")
                if new_sort_order > max_sort_order:
                    print("2")
                    new_sort_order = max_sort_order + 1

                cursor.execute("UPDATE buttons SET sort_order = 0 WHERE button_id = %s", (button_id,))


                if new_sort_order < old_sort_order: #Falls der neue Sortierwert kleiner ist als der alte
                    print (f"Moving up")
                    cursor.execute("UPDATE buttons SET sort_order = sort_order + 1 WHERE sort_order >= %s AND sort_order < %s", (new_sort_order, old_sort_order))


                elif new_sort_order > old_sort_order: #Falls der neue Sortierwert größer ist als der alte
                    print (f"Moving down")
                    cursor.execute("UPDATE buttons SET sort_order = sort_order - 1 WHERE sort_order > %s AND sort_order <= %s", (old_sort_order, new_sort_order))

                cursor.execute("UPDATE buttons SET sort_order = %s WHERE button_id = %s", (new_sort_order, button_id))
                
            # # Wenn sich die Sortierreihenfolge ändert
            # if new_sort_order != old_sort_order:
            #     if new_sort_order < old_sort_order:
            #         print ("Moving up")
            #         cursor.execute("UPDATE buttons SET sort_order = sort_order + 1 WHERE sort_order >= %s AND sort_order < %s", (new_sort_order, old_sort_order))
            #         print("Nach oben verschoben:", cursor.rowcount)
            #     else:
            #         print ("Moving down")
            #         cursor.execute("UPDATE buttons SET sort_order = sort_order - 1 WHERE sort_order > %s AND sort_order <= %s", (old_sort_order, new_sort_order))
            #         print("Nach unten verschoben:", cursor.rowcount)
                    
            # Aktualisiere den aktuellen Button
            cursor.execute(
                "UPDATE buttons SET button_name = %s, button_command = %s, sort_order = %s, button_color = %s WHERE button_id = %s",
                (new_name, new_command, new_sort_order, new_color, button_id)
            )
            
            conn.commit()
            conn.close()
            return f"Button '{new_name}' auf Position {new_sort_order} verschoben."
    # Fehlerbehandlung
    except db.Error as e:
        conn.rollback()
        conn.close()
        return f"Datenbankfehler: {e}"
    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Fehler: {e}"
        
#  Alle  Benutzer und Button Daten laden für Settings Seite
def  load_all_settings_data(active='users'):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT button_id, button_name, button_command FROM buttons")
            buttons = [{'id': row[0], 'name': row[1], 'command': row[2]} for row in cursor.fetchall()]
            cursor.execute("SELECT id, username, permission_level FROM users")
            users = [{'id': row[0], 'username': row[1], 'permission_level': row[2]} for row in cursor.fetchall()]
            cursor.execute("SELECT id, username, permission_level FROM users WHERE permission_level = 'user'")
            only_users = [{'id': row[0], 'username': row[1], 'permission_level': row[2]} for row in cursor.fetchall()]
            conn.close()
            return render_template('settings.html', users=users, buttons=buttons, active=active, only_users=only_users, publickey=publickey)
    except db.Error as e:
        print(f"Error loading buttons: {e}")
        return render_template('settings.html', users=[], buttons=[], active=active)




# Flask App initialisieren

app = Flask(__name__)
app.secret_key = SECRET_KEY
csrf = CSRFProtect(app) # CSRF Schutz aktivieren

app.config.update(
    SESSION_COOKIE_SECURE=HTTPS_ONLY, # HTTPS only
    SESSION_COOKIE_HTTPONLY=True, # Cookies nicht über JavaScript zugänglich
    SESSION_COOKIE_SAMESITE='Lax', # Cookies nur an die gleiche Seite senden
    PERMANENT_SESSION_LIFETIME=3600, # Lebensdauer der Sitzung
)

# Flask Login

# Initialisiere den LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'

# Benutzerklasse für Flask-Login
class User(UserMixin): 
    def __init__(self, id, username, permission_level):
        self.id = id
        self.username = username
        self.permission_level = permission_level

# Login-Manager erstellen
@login_manager.user_loader 
def load_user(user_id):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, permission_level FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                return User(id=user_data[0], username=user_data[1], permission_level=user_data[2])
    except db.Error as e:
        print(f"Error loading user: {e}")
    return None

login_manager.init_app(app) # Initialisiere den LoginManager mit der Flask App


# Flask-Routen


# Flask Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password_hash, permission_level FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                conn.close()
                
                if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                    user = User(id=user_data[0], username=username, permission_level=user_data[2])
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash('Ungültige Anmeldedaten')
        except db.Error as e:
            print(f"Datenbankfehler: {e}")
            flash('Datenbankfehler')
    
    return render_template('login.html')


# Flask Logout Route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Sie wurden erfolgreich abgemeldet.')
    return redirect(url_for('login'))


# Flask Index Route
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    output = None
    button_color = "#3498db"  # Standardfarbe initialisieren
    max_sort_order = get_max_sort_order()

    if request.method == 'POST':
        if 'add_button' in request.form:
            # Wenn ein neuer Button erstellt wird
            button_name = request.form.get('button_name')
            button_color = request.form.get('button_color', "#3498db")  # Standardfarbe verwenden, falls keine angegeben ist
            sort_order = request.form.get('sort_order')
            command_type = request.form.get('command_type')

            # Initialisierung des Button-Befehls
            button_command = ""

            # Abhängig von command_type setzen wir den tatsächlichen Befehl
            if command_type == "ping":
                target = request.form.get('target')
                count = request.form.get('count')
                if count == "":
                    count = 4
                button_command = f"ping {target} -c {count}"
            elif command_type == "echo":
                text = request.form.get('text')
                button_command = f"echo {text}"
            elif command_type == "nslookup":
                domain = request.form.get('domain')
                button_command = f"nslookup {domain}"
            elif command_type == "remote-execution":
                remote_command = request.form.get('remote_command')
                remote_host = request.form.get('remote_host')
                remote_port = request.form.get('remote_port', '22')
                remote_username = request.form.get('remote_username')
                
                button_command = f'ssh -i /root/.ssh/commanddeck -p {remote_port} {remote_username}@{remote_host} "{remote_command}"'
                print(f"Remote Command: {button_command}")
            elif command_type == "custom":
                custom_command = request.form.get('custom_command')
                button_command = custom_command

            # Ausgabe der Funktion, die den Button hinzufügt
            output = create_button(button_name, button_command, button_color, sort_order)
            return redirect(url_for('index'))

        elif 'pressed_button' in request.form:
            # Wenn ein existierender Button gedrückt wird
            pressed_button = request.form.get('pressed_button')
            pressed_command = request.form.get('pressed_command')
            print(f"Button '{pressed_button}' wurde gedrückt.")
            print(f"Button '{pressed_command}' wurde gedrückt.")
            try:
                result = subprocess.run(pressed_command, timeout=timeout, shell=True, text=True, capture_output=True, check=True)
                output = result.stdout
            except subprocess.TimeoutExpired:
                output = f"Error: Command took too long and was Terminated. Timeout is currently set to: " + str(timeout) + "\nYou can change the Timeout in the .env file. But i cannot be higher than 60"
            except subprocess.CalledProcessError as e:
                output = f"Command failed: {e}"

        elif 'delete_button' in request.form:
            # Wenn ein Button gelöscht wird
            button_name = request.form.get('button_name')            
            # Ausgabe der Funktion, die den Button löscht
            output = delete_button(button_name)
            return redirect(url_for('index'))
        
        elif 'modify_button' in request.form:

            print(request.form)
            # Wenn ein Button modifiziert wird
            button_id = request.form.get('button_id')
            new_name = request.form.get('button_name')  # Neuer Name
            new_command = request.form.get('command')    # Neuer Befehl
            new_sort_order = request.form.get('sort_order', 0)  # Neue Sortierreihenfolge
            new_color = request.form.get('button_color')  # Neue Farbe

            # Button in der Datenbank modifizieren
            output = modify_button(button_id, new_name, new_command, new_color, new_sort_order)
            return redirect(url_for('index'))  # Redirect zur Vermeidung von Duplicate-POSTs
            

    if current_user.permission_level  == 'admin':
        buttons= get_all_buttons()  # Wenn der Benutzer Admin ist, alle Buttons laden
    else:
        buttons = get_user_buttons(current_user.username)
    return render_template('index.html', buttons=buttons, output=output, button_color=button_color, max_sort_order=max_sort_order)

#  Flask  Settings Route

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    if request.method == 'GET':
        active = request.args.get('active', 'user')  # Default Tab User Einstellungen
        print(f"Settings GET request: active={active}, current_user={current_user.username}, permission_level={current_user.permission_level}")
        return load_all_settings_data(active=active)  # Alle Benutzer und Buttons laden
    elif request.method == 'POST':        
        if request.form.get('action') == 'getuserinfo':
            user_id = request.form.get('user_id')
            if not user_id:
                return jsonify({'error': 'No user_id provided'}), 400
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT username, permission_level, id FROM users WHERE id = %s", (user_id,))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        return jsonify({'username': row[0], 'permission_level': row[1], 'id': row[2]})
                    else:
                        return jsonify({'error': 'User not found'}), 404
                else:
                    return jsonify({'error': 'Database connection failed'}), 500
            except db.Error as e:
                return jsonify({'error': f'Database error: {e}'}), 500

        elif 'modify_user' in request.form:
            # Wenn ein Benutzer modifiziert wird
            user_id = request.form.get('user_id')
            new_username = request.form.get('username')
            new_password = request.form.get('password')
            new_permission_level = request.form.get('role')
            # print(f"Modifying user with ID: {user_id}, new username: {new_username}, new permission level: {new_permission_level}, new password: {new_password}")
            print(f'Settings POST request: {request.form}')

            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()

                    # Prüfen ob das Passwort geändert wurde
                    if new_password != "" and new_password is not None:
                        password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    else:
                        # Falls Passwort nicht geändert, aktuelles abrufen
                        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
                        password = cursor.fetchone()
                    
                    # Benutzer in der Datenbank aktualisieren

                    cursor.execute("UPDATE users SET username = %s, password_hash = %s, permission_level = %s WHERE id = %s", (new_username, password, new_permission_level, user_id))
                    conn.commit()
                    print(f"User {new_username} modified successfully.")
                    flash(f'User {new_username} modified successfully.')
                else:
                    flash('Database connection failed.')
            except db.Error as e:
                print(f'Database error: {e}')
                flash('Database error occurred while modifying user.')
            return redirect(url_for('settings'))
        
        elif 'create_user' in request.form:
            username = request.form.get('username')
            password = request.form.get('password')
            permission_level = request.form.get('role')
            print(f"Creating user with username: {username}, permission level: {permission_level}")
            if not username or not password:
                flash('Username and password are required.')
                return redirect(url_for('settings'))
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    # Prüfen ob der Benutzername schon existiert
                    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                    (count,) = cursor.fetchone()
                    if count > 0:
                        flash('Username already exists.')
                        return redirect(url_for('settings'))

                    # Passwwort verschlüsseln
                    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

                    cursor.execute("INSERT INTO users (username, password_hash, permission_level) VALUES  (%s, %s, %s)", (username, password, permission_level))
                    conn.commit()
                    flash(f'User {username} created successfully.')
                else:
                    flash('Database connection failed.')
            except db.Error as e:
                print(f'Database error: {e}')
            return redirect(url_for('settings'))
        
        elif 'delete_user' in request.form:
            user_id = request.form.get('user_id')
            username = request.form.get('username')
            if not user_id:
                print('No user selected for deletion.')
            try:
                conn = get_db_connection()
                if conn:
                    if current_user.id == int(user_id):
                        flash('You cannot delete your own account.')
                        print('User tried to delete their own account.')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    conn.commit()
                    print(f'User {username} deleted successfully.')
                else:
                    print('Database connection failed.')
            except db.Error as e:
                print(f'Database error: {e}')
                print('Database error occurred while deleting user.')
            return redirect(url_for('settings'))
        
        # In deiner settings()-Route ergänzen:
        elif request.form.get('action') == 'get_button_permissions':
            button_id = request.form.get('button_id')
            if not button_id:
                return jsonify({'error': 'No button_id provided'}), 400
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT user_id FROM user_buttons WHERE button_id = %s", (button_id,))
                    user_ids = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    return jsonify({'user_ids': user_ids})
                else:
                    return jsonify({'error': 'Database connection failed'}), 500
            except db.Error as e:
                return jsonify({'error': f'Database error: {e}'}), 500

        elif 'modify_permissions' in request.form:
            button_id = request.form.get('button_id')
            user_ids = request.form.getlist('user_permissions')
            
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()

                    # Bestehende Berechtigungen löschen
                    cursor.execute("DELETE FROM user_buttons WHERE button_id  = %s",  (button_id,))

                    if not user_ids:
                        cursor.execute("DELETE FROM user_buttons WHERE button_id = %s", (button_id,))
                        conn.commit()
                        print(f'All permissions for Button {button_id} removed successfully.')

                    # Neue Berechtigungen setzen
                    for user_id in user_ids:
                        cursor.execute("INSERT INTO user_buttons (user_id, button_id) VALUES (%s, %s)", (user_id, button_id))
                        conn.commit()
                        print(f'Permissions for User {user_id} modified successfully.')
                    
                    return redirect(url_for('settings', active='button'))
            except db.Error as e:
                print(f'Database error: {e}')
                return redirect(url_for('settings'))
            
           


        else:
            print("Unknown action in settings form: ", request.form)
            return redirect(url_for('settings'))
        
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=int(web_port))