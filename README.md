# Simply Watchdog 🛡️👁️

**Simply Watchdog** is an AI-powered system monitoring tool for real-time visibility and threat detection.
![Dashboard Preview](ui/app_icon.png)

## 🚀 Features

*   **Real-Time Monitoring**: Live tracking of CPU, Memory, Disk I/O, and Network Traffic.
*   **AI Threat Detection**: Heuristic and Machine Learning-based analysis of process behavior and network connections to detect anomalies (Shells, C2 beacons, etc.).
*   **Deep Scan**: On-demand file system and process scanning.
*   **Network Sniffer**: Visualizes active connections with GeoIP data and whitelisting capabilities.
*   **Process Explorer**: Hierarchical view of running services and applications.
*   **Glassmorphism UI**: A fully custom, high-performance GUI with a Neon/Dark theme.

## 🛠️ Installation

### Prerequisites
*   Windows 10/11
*   Python 3.10+

### Setup
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/SimplyWatchdog.git
    cd SimplyWatchdog
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Requires `psutil`, `PySide6`, `scikit-learn`, `watchdog`, etc.)*

## ⚡ Usage

### Running the App
You can launch the application primarily via the Python entry point:

```bash
python main.py
```

### Configuration
*   **Settings Menu**: Click the "Gear" icon in the header to adjust update intervals and manage filters.
*   **Filters**:
    *   **Ignored IPs**: Whitelist specific IP addresses to stop them from appearing in alerts.
    *   **Ignored Services**: Whitelist known safe processes.
    *   *Tip: Use the Checklist in Settings > Filters to easily add currently active items.*

## 📂 Project Structure

*   `main.py`: Entry point.
*   `ui/`: GUI components (Dashboard, Widgets, Header).
*   `monitors/`: Backend monitoring threads (Process, Network, Resource, FS).
*   `core/`: Event bus and core logic.
*   `ai/`: Detection engine and anomaly models.
*   `config/`: JSON configuration and settings handling.

## ⚠️ Disclaimer
This tool is intended for system administration and educational purposes. The AI detection is probabilistic; always verify alerts manually.

---
*v1.0.0 Release - Sentinel Protocol Active*
