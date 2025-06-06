


// Sicherstellen, dass der Header responsive bleibt
function adjustHeaderLayout() {
    const header = document.querySelector('header');
    if (window.innerWidth < 768) {
        header.style.flexDirection = 'column';
        header.style.height = 'auto';
        header.style.padding = '10px';
    } else {
        header.style.flexDirection = 'row';
        header.style.height = '70px';
        header.style.padding = '0 20px';
    }
}


function togglesidebar_right() {
    const sidebar_right = document.querySelector('.sidebar_right');
    const overlay = document.querySelector('.sidebar_right-overlay');
    sidebar_right.classList.toggle('active');
    overlay.style.display = sidebar_right.classList.contains('active') ? 'block' : 'none';
}

function toggleCreateUserPopup() {
    const overlay = document.getElementById('CreateUserPopup');
    overlay.classList.toggle('show');
}

function toggleModifyUserPopup(user_id = '') {
    const overlay = document.getElementById('ModifyUserPopup');
    overlay.classList.toggle('show');

    if (user_id) {
        fetch('/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: `action=getuserinfo&user_id=${encodeURIComponent(user_id)}`
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('modify_username').value = data.username;
                document.getElementById('modify_role').value = data.permission_level;
                document.getElementById('modify_user_id').value = user_id;
            } else {
                alert(data.error);
            }
        });
    }
}

function toggleDeleteUserPopup(user_id = '') {
    const overlay = document.getElementById('DeleteUserPopup')
    overlay.classList.toggle('show')

    if (user_id) {
        fetch('/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: `action=getuserinfo&user_id=${encodeURIComponent(user_id)}`
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('delete_user_id').value = user_id;
                document.getElementById('delete_username_original').value = data.username;
            } else {
                alert(data.error);
            }
        });
    }
}

function togglePermissionsButtonPopup(button_id = '') {
    const overlay = document.getElementById('ModifyPermissionsPopup');
    overlay.classList.toggle('show');
    if (button_id) {
        document.getElementById('modify_button_id').value = button_id;

        // Alle Checkboxen erstmal deaktivieren
        document.querySelectorAll('#ModifyPermissionsPopup input[type="checkbox"][name="user_permissions"]').forEach(cb => {
            cb.checked = false;
        });

        // Berechtigte user_ids vom Backend holen und Checkboxen setzen
        fetch('/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: `action=get_button_permissions&button_id=${encodeURIComponent(button_id)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.user_ids) {
                data.user_ids.forEach(uid => {
                    const checkbox = document.getElementById('permission_' + uid);
                    if (checkbox) {
                        checkbox.checked = true; // Checkbox setzen[7]
                    }
                });
            }
        });
    }
}




// CSRF-Handler für Fetch-Requests
function getCSRFToken() {   
    return document.querySelector('meta[name="csrf-token"]').content;
}


function toggleUserSettings() {
    // const overlay_buttons = document.getElementById('settings_buttons');
    // overlay_buttons.classList.remove('show');
    // const overlay = document.getElementById('settings_user');
    // overlay.classList.add('show');
    window.location.href  = "/settings?active=user";
}

function toggleButtonSettings() {
    // const overlay_users = document.getElementById('settings_user');
    // overlay_users.classList.remove('show');
    // const overlay = document.getElementById('settings_buttons');
    // overlay.classList.add('show');
    window.location.href  = "/settings?active=button";

}

function toggleSystemSettings() {
    window.location.href = "/settings?active=system";
}

document.addEventListener('DOMContentLoaded', function() {
    const deleteUserForm = document.getElementById('deleteUserForm');
    if (deleteUserForm) {
        deleteUserForm.addEventListener('submit', function(event) {
            
            // Werte auslesen
            const original = document.getElementById('delete_username_original').value.trim();
            const input = document.getElementById('delete_username').value.trim();

            // Prüfen, ob die Usernamen übereinstimmen
            if (original !== input) {
                event.preventDefault(); // Formular-Submit verhindern
                alert('Der eingegebene Username stimmt nicht mit dem Original überein!');
            }
            // sonst wird das Formular ganz normal abgeschickt
            
        });
    }
});




