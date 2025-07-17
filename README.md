# Features

- Einfache Weboberfläche zur Verwaltung und Ausführung von Befehlen
- Anpassbare Benutzerrechte pro Button
- Übersichtliche Darstellung der angelegten Aktionen (Buttons)
- Benutzerverwaltung mit verschiedenen Berechtigungsstufen (Admin, User)
- Visuelle Anpassung der Buttonfarbe je nach Funktion
- Möglichkeit, Buttons zu erstellen, zu bearbeiten oder zu löschen
- Zuweisung von Benutzerrechten für einzelne Buttons
- Sicherer Login-Screen für Benutzer-Authentifizierung
- Unterstützung von Remote-Befehlen via SSH
- Integration einer SQL-Datenbank zur Speicherung von Einstellungen und Nutzerdaten

---

![Anmeldemaske: Sicheres Login für Benutzer](https://github.com/g-silvan/CommandDeck/media/login_screen.png)

![Dashboard (Admin): Übersicht und Ausführung der wichtigsten Aktionen](https://github.com/g-silvan/CommandDeck/media/dashboard_admin.png)

![Ansicht: Aktionen ohne Bearbeitungsmodus](https://github.com/g-silvan/CommandDeck/media/dashboard_user.png)

![Vergabe von individuellen Button-Berechtigungen pro Benutzer](https://github.com/g-silvan/CommandDeck/media/button_permissions.png)

![Benutzerübersicht und Verwaltung von Accounts](https://github.com/g-silvan/CommandDeck/media/users.png)

---

# Installation

## 1. Install Python 3 and pip

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```


---

## 2. Install MariaDB and MariaDB Connector

```bash
sudo apt install -y mariadb-server libmariadb3 libmariadb-dev
sudo systemctl start mariadb
sudo systemctl enable mariadb
```


---

## 3. Secure MariaDB (Optional, Recommended)

```bash
sudo mysql_secure_installation
```

Follow the prompts to set a root password and secure your installation.

---

## 4. Create a Database User

Log in to MariaDB as root:

```bash
sudo mysql -u root -p
```

Execute the following commands in the MariaDB shell:
Change the Username & Password!

```sql
CREATE USER 'commanddeck_user'@'localhost' IDENTIFIED BY 'commanddeck_password';
CREATE DATABASE commanddeck_database;
GRANT ALL PRIVILEGES ON commanddeck_database.* TO 'commanddeck_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```


---

## 5. Import the Database Schema

Import the `database.sql` file into your new database:

```bash
cd CommandDeck
mysql -u commanddeck_user -p commanddeck_database < database.sql
```


---

## 6. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```


---

## 7. Install Python Requirements Inside Virtual Environment

```bash
pip install -r requirements.txt
```


---

## 8. Create an SSH Key (for Remote Execution)

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -f ~/.ssh/commanddeck_key -N ""
chmod 600 ~/.ssh/commanddeck_key ~/.ssh/commanddeck_key.pub
```


---

## 9. Configure the `.env` File

Edit your `.env` file and update the following values:

```ini
DB_USER="commanddeck_user"
DB_PASSWORD="commanddeck_password"
DB_NAME="commanddeck_database"
DB_HOST="localhost"

# SECRET_KEY must be updated to a strong, unique value
SECRET_KEY=your_strong_secret_key_here

# Set the path and name for your SSH key (used for remote execution)
SSH_KEY_PATH=/home/youruser/.ssh/commanddeck_key
PUBLIC_SSH_KEY_PATH=/home/youruser/.ssh/commanddeck_key.pub

# Set the port for the web interface
WEB_PORT=8081

# Set to true if you want to enable HTTPS
HTTPS_ENABLED=false

# Set the timeout
TIMEOUT=5
```


---

## 10. Make Scripts Executable

```bash
chmod a+x create_admin.sh
chmod a+x start.sh
```


---

## 11. Run the Admin Creation Script

Finally, to create a default admin account:

```bash
./create_admin.sh
```


---

## 12. Start CommandDeck

**Start your CommandDeck:**

```bash
./start.sh
```

**All steps completed! Your application is now ready to use with the default admin account.**

**Credentials for default Admin user:**

**Username: admin**

**Password: commanddeck**
