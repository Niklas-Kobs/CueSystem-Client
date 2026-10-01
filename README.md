<img width="1280" height="640" alt="Git_Repo_Coverart-3" src="https://github.com/user-attachments/assets/9f2be600-95cd-4f68-8b60-32e94d6026d0" />


Welcome to **CueSystem-Client (PyWebView GUI)**, a PyWebView GUI application with local SQLite database integration and API sync capabilities for managing patient queues!

This desktop application allows staff to manage patient lists, update queue positions, trigger patient calls, and sync current waiting room status to a remote display web server.

## Key Features

* **Desktop Application Interface:** Native desktop GUI built using `pywebview`, loading local HTML/JS assets (`gui/index.html`).

* **SQLite Database Storage:** Persists full patient records (patient ID, name, room, infos, doctor, duration, call status, timestamp) locally in `queue.db`.

* **Full Queue Management:**
  * Add, edit, remove, and reorder patients (move up/down, move to top, move to end).
  * Toggle patient call/status flags (`is_called`).
  * Automatic database cleanup of historical entries older than the current day.

* **API & Web Server Synchronization:**
  * Synchronizes the top 5 queue positions with the central web server via HTTP POST (`/update`).
  * Sends popup/announcement notifications (`/message`).
  * Triggers remote execution commands (`/execute`).
  * Live heartbeat/connectivity checks (`/alive`).

* **Configurable Settings:** Dynamically manages system settings (API URLs, preset message templates, doctor assignments) using `jsonLib`.

## Installation & Requirements

### Dependencies

Ensure you have Python installed, along with the required third-party libraries:

```
pip install pywebview requests
```

### Running the Application

To start the desktop management interface, run:

```
python app.py
```

## API Methods (JavaScript Bridge)

The `WartelisteAPI` class exposes Python methods to the JavaScript frontend via `pywebview`:

* `get_queue()` — Fetches all patient records from `queue.db`.
* `add_full_patient(data)` — Adds a new patient entry.
* `add_at_position(data, target_index)` — Inserts a patient at a specific position.
* `save_patient_edit(data)` — Updates existing patient details.
* `remove_entry(index)` — Removes a patient by index.
* `move_entry(index, direction)` — Swaps positions up or down.
* `move_to_top(index)` / `move_to_end(index)` — Shifts patients to top or bottom.
* `toggle_call_status(index)` — Toggles call status (`1` / `0`).
* `refresh()` — Reads top 5 patients from SQLite and sends update payloads to the central display API.
* `send_message(subject, message)` — Sends emergency or status popups to the display server.
* `update_url(url_data)` — Dynamically updates the backend API base URL.
* `check_data()` — Cleans up entries prior to today.

## Support & Feedback

For technical issues or configuration help, please open an issue or contact your system administrator.
