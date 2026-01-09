# PaperPrep (local development)

This document explains how to set up the Python environment and how to build the Tailwind CSS used by the site.

## Python (backend)

1. Create and activate a virtual environment (PowerShell):

```powershell
cd C:\Users\User\Downloads\paperprep_project\paperprep
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the Flask app:

```powershell
python app.py
```

The site will be available at `http://127.0.0.1:5000/`.

## Tailwind CSS (frontend)

To avoid using the Tailwind CDN in production, build a local CSS file. This project includes a minimal `package.json` and `src/styles.css`.

1. Install Node.js (if not already installed).
2. From the project root run:

```powershell
npm install
```

3. Build the production CSS once:

```powershell
npx tailwindcss -i ./src/styles.css -o ./static/css/tailwind.css --minify
```

Or use the npm script:

```powershell
npm run build:css
```

4. For development, run a watcher:

```powershell
npm run watch:css
```

Notes
- `tailwind.config.js` is set to scan the `templates/` directory and `app.py` for used classes. If you add more files, update the `content` array accordingly.
- If you prefer the CDN for quick development, `templates/base.html` originally included the Tailwind CDN snippet. For production, compile and serve `static/css/tailwind.css` instead.

---

If you want, I can also add a small PowerShell script to build and run everything in one step. Would you like that?