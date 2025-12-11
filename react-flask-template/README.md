# React + Flask Full-Stack Template

Template proyek full-stack dengan React sebagai frontend dan Flask sebagai backend REST API.

## Struktur Proyek

```
react-flask-template/
├── backend/                 # Flask Backend (Port 5000)
│   ├── main.py             # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (optional)
├── frontend/               # React Frontend (Port 3000)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.js         # Main App component
│   │   └── index.js       # Entry point
│   ├── package.json        # Node dependencies
│   └── public/            # Static files
└── README.md              # This file
```

## Instalasi

### Backend (Flask)

1. Masuk ke folder backend:
```bash
cd backend
```

2. Buat virtual environment (opsional tapi disarankan):
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Frontend (React)

1. Masuk ke folder frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Menjalankan Aplikasi

### Menjalankan Backend (Flask)

1. Masuk ke folder backend:
```bash
cd backend
```

2. Aktifkan virtual environment (jika menggunakan):
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Jalankan Flask server:
```bash
python main.py
```

Backend akan berjalan di `http://localhost:5000`

### Menjalankan Frontend (React)

1. Masuk ke folder frontend:
```bash
cd frontend
```

2. Jalankan React development server:
```bash
npm start
```

Frontend akan berjalan di `http://localhost:3000`

## API Endpoints

### GET /api/hello
Mengembalikan pesan hello dari backend.

**Response:**
```json
{
  "message": "Hello from Flask Backend!",
  "status": "success"
}
```

## Menjalankan Keduanya Secara Bersamaan

Buka 2 terminal:

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## CORS

Backend sudah dikonfigurasi untuk mengizinkan request dari frontend React (localhost:3000) menggunakan Flask-CORS.

## Catatan

- Pastikan backend berjalan sebelum frontend melakukan request
- Backend berjalan di port 5000
- Frontend berjalan di port 3000
- Frontend akan otomatis melakukan proxy request ke backend jika dikonfigurasi di `package.json`

