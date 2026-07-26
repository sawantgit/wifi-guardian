# Wi-Fi Guardian 🛡️

Wi-Fi Guardian is a fast, automated home network security monitor and intrusion detection system. It scans your local subnet for active host devices, compares them against a list of trusted endpoints in an SQLite database, and alerts you of any unknown/unrecognized devices (intruders) in real time via a sleek, modern glassmorphic dashboard.

---

## Features
- **Real-Time Subnet Scanning**: Automatically discovers all live devices on your local network.
- **Dual-Mode Scan Engine**:
  - **Standard Mode**: Performs high-fidelity Layer 2 ARP discovery using Scapy.
  - **Fallback Mode (High Performance)**: If WinPcap/Npcap is missing or when running without admin privileges on Windows, it automatically falls back to an optimized single-socket UDP sweep and reads the OS ARP table.
- **Visual Intruder Alerts**: A pulsing alert banner triggers visually when an unrecognized device connects.
- **Device Management**: Quickly label and mark devices as trusted or remove trust with a single click.
- **Glassmorphic UI**: High-end dark theme dashboard with responsive counters, animated hover transitions, and a radar scanning visual overlay during re-scans.
- **Instant Loads**: Built-in 15-second scanning caching so your app loads instantly during active modifications.

---

## Installation & Setup

Follow these steps to run the project locally on your machine:

### 1. Prerequisites
- **Python**: Python 3.10+ installed.
- *(Optional)*: Install [Npcap](https://npcap.com/) or [WinPcap](https://www.winpcap.org/) on Windows. If not installed, the application will automatically run in Fallback Mode.

### 2. Clone the Repository
```bash
git clone https://github.com/sawantgit/wifi-guardian.git
cd wifi-guardian
```

### 3. Create a Virtual Environment
```bash
python -m venv venv
```
Activate the environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
Install the required packages (`Flask` and `Scapy`):
```bash
pip install flask scapy
```

### 5. Run the Application
Start the local development server:
```bash
python app.py
```

Open your web browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## How It Works
1. When you open the dashboard or click **Refresh Scan**, the app detects your local IP and subnet range (e.g. `192.168.1.0/24`).
2. The scanner sends out packets to discover hosts (`scanner.py`).
3. The live IPs and MAC addresses are matched against the local SQLite database (`database.db`).
4. If any MAC address is not registered in the database, the dashboard displays an **Intruder Warning**.
5. You can type a label (e.g., "My Phone") and click **Trust Device** to authorize the device.
