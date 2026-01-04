# mini_prtg 🚦📊

A **lightweight network traffic monitoring system (Mini PRTG)** written in Python.  
This project is designed for learning purposes, small labs, and personal monitoring needs, with a clean and modular structure.

---

## ✨ Features

- 📡 Network traffic (bandwidth) collection
- 🗄️ Data storage using SQLite
- 🧩 Modular project structure (`collector`, `storage`, `ui`)
- 🖥️ Simple user interface
- ⚡ Lightweight and easy to extend

---

## 🗂️ Project Structure

```text
mini_prtg/
├── collector/        # Traffic / SNMP data collection logic
├── storage/          # Data storage and database handling
├── ui/               # User interface
├── main.py           # Application entry point
├── traffic.db        # SQLite database (ignored by git)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## 🛠️ Requirements

- Python 3.9 or newer
- pip

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone git@github.com:Darvsih1989/mini_prtg.git
cd mini_prtg
```

### 2️⃣ Create and activate a virtual environment (recommended)

```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
python main.py
```

The application will start collecting and displaying network traffic data based on the configured collectors.

---

## 🧪 Development Notes

- `traffic.db` is generated automatically at runtime and should **not** be committed to Git.
- You can extend the project by adding new collectors or UI components.
- The codebase is intentionally simple and readable.

---

## 🚀 Roadmap (Ideas)

- Web-based dashboard
- Authentication
- Alerting (threshold-based notifications)
- Export data to CSV / JSON

---

## 🤝 Contributing

Contributions, ideas, and improvements are welcome:

1. Fork the repository
2. Create a new branch (`feature/my-feature`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

This project is released under the **MIT License**.

---

## 👤 Author

**MohamadReza Darvishi**  
GitHub: https://github.com/Darvsih1989

