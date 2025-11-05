## TechStore 

### Ce este proiectul
TechStore este o aplicație tip magazin de electronice cu:
- Backend REST în Python (FastAPI) pentru autentificare simplă, listă produse și recomandări bazate pe profilul utilizatorului
- Frontend React (Create React App + CRACO) cu component library (Radix UI), Tailwind CSS și hooks simple

Aplicația poate rula fără bază de date (date hardcodate). Opțional, poate utiliza MongoDB prin `motor`/`pymongo` dacă sunt setate variabilele de mediu.

### Tehnologii folosite
- Backend: FastAPI, Uvicorn, Pydantic v2, CORS middleware, `python-dotenv`, (opțional) Motor/MongoDB
- Frontend: React 18, CRACO, Tailwind CSS, Radix UI, React Router, Axios
- Tools/dev: ESLint, Prettier (implicit CRA), Pytest (pentru backend), Black/Isort/Flake8 (config în requirements)

### Structura proiectului
- `backend/` – aplicația FastAPI (`server.py`), `requirements.txt`
- `frontend/` – aplicația React (CRA + CRACO), `src/` cu componente UI

### API – endpoint-uri principale (backend)
Baza: `http://localhost:8000`
- `GET /` – health/basic message
- `POST /api/auth/login` – login cu user hardcodat; body: `{ "username", "password" }`
- `GET /api/products` – lista de produse
- `GET /api/products/{product_id}` – detalii produs
- `GET /api/recommendations/{user_id}` – primele 3 recomandări pe baza profilului
- `GET /api/debug/db` – info de debug (fără parole), plus flag conexiune Mongo

Model utilizator/profil și produse sunt definite în `backend/server.py`. Dacă nu este configurat MongoDB, aplicația folosește liste în memorie.

### Variabile de mediu (opțional)
În directorul `backend/`, se poate crea fișier `.env`:
- `MONGO_URL` – conexiune MongoDB (ex. `mongodb://localhost:27017`)
- `DB_NAME` – numele bazei
- `CORS_ORIGINS` – liste separate prin virgulă (ex. `http://localhost:3000,http://localhost:5173`); implicit `*`

### Cum rulez – Backend
Necesită Python 3.11+.
1) În terminal:
```
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```
2) (Opțional) creați `.env` cu valorile dorite
3) Porniți serverul:
```
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```
Serverul va rula pe `http://localhost:8000`.

Teste rapide:
```
curl http://localhost:8000/
curl http://localhost:8000/api/products
```

### Cum rulez – Frontend
Necesită Node 18+ (recomandat) și npm.
1) În terminal:
```
cd frontend
npm ci
npm start
```
2) Aplicația pornește pe `http://localhost:3000` (CRACO). Frontend-ul consumă API-ul de pe `http://localhost:8000`.

### Notițe despre datele demo
- Utilizatori demo (hardcodate) sunt în `backend/server.py` (de ex. `Elvis_Marcu` / `pass123`)
- Produsele sunt hardcodate și acoperă categorii precum `laptops`, `smartphones`, `gaming`, `audio`, `fitness`.
- Algoritmul de recomandări calculează un scor din interese, branduri preferate și buget, apoi returnează top 3.

### Build/Prod (succint)
- Frontend: `cd frontend && npm run build` (generează `build/`)
- Backend: se rulează cu Uvicorn/ASGI sau containerizat; necesită aceleași variabile de mediu

### Probleme cunoscute / simplificări
- Login-ul este doar de demo (fără JWT), parole în clar pentru test; nu pentru producție
- Persistența MongoDB este opțională și nu este obligatorie pentru rulare
