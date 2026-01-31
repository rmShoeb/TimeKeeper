# TimeKeeper Build Scripts

This directory contains cross-platform build scripts for setting up and running the TimeKeeper application.

## Available Scripts

### Setup Scripts

**Windows:**
```cmd
build\setup.bat
```

**Linux/macOS:**
```bash
chmod +x build/setup.sh
./build/setup.sh
```

**What it does:**
1. Checks for Python 3.10+ and Node.js 18+ installation
2. Creates Python virtual environment in `backend/venv`
3. Installs Python dependencies from `backend/requirements.txt`
4. Creates `.env` file from `.env.example` (if not exists)
5. Installs Node.js dependencies in `frontend/`

### Run Scripts

**Windows:**
```cmd
build\run.bat
```

**Linux/macOS:**
```bash
chmod +x build/run.sh
./build/run.sh
```

**What it does:**
1. Starts FastAPI backend on http://localhost:8000
2. Starts Angular frontend on http://localhost:4200
3. Keeps both servers running until Ctrl+C is pressed

## First Time Setup

1. **Clone or download the project**

2. **Run the setup script** for your platform:
   - Windows: Double-click `setup.bat` or run from command prompt
   - Linux/macOS: Run `./build/setup.sh` from terminal

3. **Update environment variables**:
   - Edit `backend/.env` file
   - Generate a secure JWT secret key:
     ```python
     # In Python
     import secrets
     print(secrets.token_urlsafe(32))
     ```
   - Replace `JWT_SECRET_KEY` value in `.env` with the generated key

4. **Run the application**:
   - Windows: Double-click `run.bat` or run from command prompt
   - Linux/macOS: Run `./build/run.sh` from terminal

5. **Access the application**:
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Prerequisites

### Required Software

- **Python 3.10+**: Download from https://python.org
- **Node.js 18+**: Download from https://nodejs.org
- **Angular CLI 18+**: Install globally with `npm install -g @angular/cli@18`

### Platform-Specific Notes

**Windows:**
- Make sure Python and Node.js are added to PATH during installation
- Run scripts from Command Prompt or PowerShell

**Linux/macOS:**
- Make scripts executable: `chmod +x build/*.sh`
- May need to install `python3-venv` package on some Linux distributions:
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-venv

  # Fedora
  sudo dnf install python3-virtualenv
  ```

## Troubleshooting

### Python Not Found
- **Windows**: Ensure Python is installed and in PATH. Try `py` instead of `python`
- **Linux/macOS**: Install Python 3: `sudo apt install python3` (Ubuntu/Debian)

### Node.js Not Found
- Install from https://nodejs.org
- Verify installation: `node --version` and `npm --version`

### Port Already in Use
- **Backend (8000)**: Change port in `run` script, update CORS settings
- **Frontend (4200)**: Run `ng serve --port 4201` manually

### Virtual Environment Issues
- Delete `backend/venv` folder and re-run setup script
- On Windows, ensure execution policy allows scripts:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Angular Build Errors
- Clear node_modules: `rm -rf frontend/node_modules`
- Clear npm cache: `npm cache clean --force`
- Re-run setup script

### Database Initialization Errors
- Delete `backend/timekeeper.db` file
- Restart backend server

## Manual Setup (Alternative)

If automated scripts don't work, follow these manual steps:

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS

# Run backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm start
```

## Development Tips

### Backend Development
- API docs available at: http://localhost:8000/docs
- Hot reload enabled (changes reflect automatically)
- Check console for scheduler logs (runs at 9 AM Bangladesh Time)

### Frontend Development
- Hot reload enabled (changes reflect automatically)
- Mobile view: Use browser DevTools (F12) → Toggle device toolbar
- Bootstrap 5 classes available globally

### Building for Production

**Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Output in: frontend/dist/
```
