Welcome to **Queue System v2.0**, a lightweight patient management and queue display solution designed to streamline waiting room management and real-time status updates!

Manage patient queues via a desktop GUI, synchronize data across web endpoints, and trigger live popups or status calls directly on waiting room screens.

---

## Key Features

- **Desktop GUI Management:** Native desktop interface powered by `pywebview` for managing patients and queue order.
- **SQLite Database Backend:** Persistent storage for queue data with automatic cleanup of old entries.
- **Real-Time Web API & Server:** Built-in Flask/Waitress server to stream live queue status (`/show`) to web interfaces.
- **Dynamic Reordering:** Easily move patients up, down, to the top, or to the end of the queue.
- **Popup & Call Notification System:** Send custom messages and call triggers directly to the display interface via API endpoints.
- **Configuration Management:** Integrated configuration handling using `jsonLib`.

---

## Installation & Setup

### Prerequisites

Make sure you have Python installed, then install the required dependencies:

```bash
pip install flask waitress pywebview requests
```

*(Ensure your custom `jsonLib` module is placed in the project root directory.)*

### Running the Application

1. **Start the Web Display Server (Backend API):**
   ```bash
   python server.py
   ```
   *The server runs on port `55000` by default using Waitress.*

2. **Start the Desktop Management App (GUI):**
   ```bash
   python main.py
   ```

---

## How to Use

1. Launch the Server and Desktop Application.
2. **In the Desktop App:**
   - Add new patient entries with details (ID, Name, Room, Doctor, Duration).
   - Reorder queue entries or toggle call statuses.
   - Click refresh/sync to send updated queue data to the web display server.
   - Send popup notifications or pop messages to waiting room displays.
3. **On the Waiting Room Display:**
   - Open a browser pointing to the server root URL (`http://<server-ip>:55000/`) to view real-time patient queue updates.

---

## Feedback & Bug Reporting

Found an issue with queue syncing or have a feature request? Please open an issue on GitHub or contact the system administrator!
