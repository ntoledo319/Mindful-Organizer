# Building for Windows

## Prerequisites
- Windows 10/11
- Python 3.9+
- Git

## Setup
1. Clone the repo.
2. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Build Executable
Run the PyInstaller command to create a single-file executable:

```powershell
pyinstaller --name "MindfulOrganizer" --windowed --onefile --icon=resources/icon.ico --add-data "src/config;config" src/main.py
```

## Output
The executable will be in `dist/MindfulOrganizer.exe`.

## Store Packaging
To package for the Microsoft Store (MSIX):
1. Install the [MSIX Packaging Tool](https://apps.microsoft.com/store/detail/msix-packaging-tool/9N5LW3JBCXKF).
2. Run the tool and point it to the `MindfulOrganizer.exe` installer (or create a simple installer script).
3. Sign the package with your developer certificate.
