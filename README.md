# Buggy Minesweeper — Seriously, just think about it

## Saper_kursach Project Deployment Guide

A short practical guide for cloning the repository and setting up an isolated Python virtual environment (`venv`).

### Prerequisites

* Git (download from [git-scm.com](https://git-scm.com?utm_source=chatgpt.com))
* Python 3.x (download from [python.org](https://www.python.org?utm_source=chatgpt.com))

> Note: All required dependencies are installed automatically by the code itself, so there is no need to manually install requirements.

---

## Step-by-Step Setup

### 1. Clone the Repository

Open a terminal (or command prompt) and run:

```bash
git clone https://github.com/TheInfani/Saper_kursach.git
```

---

### 2. Navigate to the Project Directory

```bash
cd Saper_kursach
```

---

### 3. Create a Virtual Environment

Create an isolated environment named `venv`:

```bash
python -m venv venv
```

---

### 4. Activate the Virtual Environment

Activate the environment depending on your operating system:

#### Windows (Command Prompt)

```bash
venv\Scripts\activate.bat
```

#### Windows (PowerShell)

```bash
venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
source venv/bin/activate
```

After successful activation, you should see `(venv)` at the beginning of your terminal line.

---

### 5. Run the Application

Run the main project script (usually `main.py` or `index.py`):

```bash
python main.py
```

---

## Deactivating the Environment

When you are done working with the project, deactivate the virtual environment with:

```bash
deactivate
```
