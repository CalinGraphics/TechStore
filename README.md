## TechStore – Intelligent Electronics Store

TechStore este o aplicație completă tip magazin de electronice, construită pentru laborator / proiect de facultate, care pune accent pe:
- recomandări personalizate pe baza profilului utilizatorului,
- căutare avansată în colecția de produse,
- căutare full‑text în fișele tehnice folosind modele IR de tip Lucene (TF‑IDF / BM25),
- o experiență de UI modernă, „gata de demo” pentru GitHub.

---

### Ce face aplicația

- **Autentificare & profil utilizator**
  - Login / register cu profil bogat (vârstă, buget, interese, branduri preferate).
  - Editare profil, avatar custom și salvarea preferințelor.

- **Catalog de produse**
  - Listă de produse pe categorii (laptops, smartphones, gaming, audio, fitness etc.).
  - Detaliu de produs cu descriere, fișă tehnică, stoc, furnizor și livrare.
  - Coș de cumpărături, checkout cu date de livrare și istoric de comenzi.

- **Recomandări & IR**
  - Recomandări „Pentru tine” în funcție de interese, buget și branduri preferate.
  - Recomandări de **produse similare** pe pagina de detaliu, bazate pe similaritate cosinus între vectori TF‑IDF.

- **Căutare avansată**
  - Căutare generală în colecția de produse:
    - index intern, full‑text, scorare TF‑IDF / BM25,
    - filtrare după categorie și ordonare după scor (asc / desc).
  - Căutare predictivă / **autocomplete** în titlurile produselor (prefix search, trigram similarity, Edit Distance – Levenshtein).
  - Căutare în **fișele tehnice** (specs + descriere):
    - pagină separată „Căutare în specificații”,
    - scor Lucene‑style (TF‑IDF / BM25) și explicație textuală a modului de calcul.

- **Mod demo fără DB**
  - Poate rula complet cu date hardcodate (utilizatori + produse).
  - Integrare opțională cu Supabase pentru persistare reală (utilizatori, produse, favorite, comenzi).

---

### Stack tehnic

- **Backend**
  - Python 3.11+, **FastAPI** (API REST, routing, validare).
  - **Pydantic v2** – modele pentru utilizatori, produse, comenzi.
  - Motor IR custom în `app/search_engine.py`:
    - tokenizare,
    - TF‑IDF,
    - BM25 (formulă compatibilă cu Lucene),
    - similaritate cosinus.
  - Integrare opțională cu **Supabase** (Postgres) + fallback pe liste in‑memory.
  - Uvicorn, CORS middleware, `python-dotenv`.

- **Frontend**
  - **React 18** (Create React App + CRACO).
  - Design sistem bazat pe Radix UI / shadcn components:
    - carduri, tabs, dialog, sheet, badge, input etc.
  - React Router pentru routing (login, dashboard, profil, detalii produs, comenzi).
  - Axios pentru consumarea API‑ului.

- **Dev & tooling**
  - Backend: `black`, `isort`, `flake8`, `pytest`.
  - Frontend: ESLint / Prettier (implicit CRA).

---

### Structura proiectului

- `backend/`
  - `server.py` – aplicația FastAPI principală.
  - `app/`
    - `routes/` – endpoint‑uri (`auth`, `products`, `recommendations`, `favorites`, `orders`, `debug`).
    - `models.py` – modele Pydantic (User, Product, Recommendation, Order etc.).
    - `data.py` – utilizatori și produse demo + helperi pentru stoc / tags.
    - `database.py` – integrare Supabase + fallback in‑memory.
    - `search_engine.py` – motorul IR (TF‑IDF, BM25, cosine similarity).
    - `services.py` – business logic (buget, scor recomandări).
    - `config.py` – setări aplicație.
  - `requirements.txt` – dependențe backend.

- `frontend/`
  - `src/App.js` – aplicația React, routing, dashboard, UI principal.
  - `src/components/ui/` – bibliotecă de componente UI reutilizabile.
  - `src/index.js`, `index.css`, `App.css` – bootstrap și styling global.

---

### API – endpoint‑uri esențiale

Bază: `http://localhost:8000`

- **Health / config**
  - `GET /` – mesaj simplu („Hello World!”).
  - `GET /health` – health check + info de config.

- **Auth & profil**
  - `POST /api/auth/login` – autentificare (demo: user hardcodat / Supabase).
  - `POST /api/auth/register` – înregistrare user cu profil.
  - `PUT /api/profile/{user_id}` – update profil (vârstă, buget, interese, branduri, username).

- **Produse**
  - `GET /api/products` – listă produse (filtrare `category`, `active_only`).
  - `GET /api/products/{product_id}` – detalii produs.
  - `GET /api/categories` – categorii distincte.
  - `POST /api/products` (admin) – creare produs.
  - `PUT /api/products/{product_id}` (admin) – update produs.
  - `DELETE /api/products/{product_id}` (admin) – ștergere produs.

- **Căutare & IR**
  - `GET /api/products/search?q=&method=&order=` – căutare full‑text în colecția de produse (TF‑IDF / BM25, asc/desc).
  - `GET /api/products/autocomplete?q=` – autocomplete căutare predictivă în titluri.
  - `GET /api/products/similar/{product_id}?limit=` – produse similare pe baza similarității cosinus.
  - `GET /api/spec-search?q=&method=&order=` – căutare în fișele tehnice (specs) cu scor Lucene‑style.

- **Recomandări & favorite**
  - `GET /api/recommendations/{user_id}` – recomandări personalizate.
  - `GET /api/favorites/{user_id}` / `POST` / `DELETE` – gestiune produse favorite.

- **Comenzi**
  - `POST /api/transactions` – checkout și creare comandă.
  - `GET /api/orders/{user_id}` – istoricul comenzilor.

---

### Configurare & rulare

#### Backend (FastAPI)

Necesită Python **3.11+**.

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

Variabile de mediu (opțional, pentru Supabase / CORS):

- Copiază `backend/.env.example` → `backend/.env`
- Copiază `frontend/.env.example` → `frontend/.env` (opțional)

- `SUPABASE_URL`, `SUPABASE_KEY` – conexiune Supabase.
- `CORS_ORIGINS` – liste separate prin virgulă (ex. `http://localhost:3000,http://localhost:5173`).

Pornire server:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Teste rapide:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/products
curl "http://localhost:8000/api/products/search?q=laptop&method=bm25"
```

#### Frontend (React)

Necesită Node **18+**.

```bash
cd frontend
npm ci          # sau npm install
npm start
```

Aplicația React pornește în mod implicit pe `http://localhost:3000` și consumă API‑ul de pe `http://localhost:8000`.

Build de producție:

```bash
cd frontend
npm run build
```

---

### Date demo

- Utilizatori demo (hardcodați) – vezi `backend/app/data.py`:
  - `admin` / `admin123` (role: admin)
  - `user` / `pass123` (role: user)
- Produse demo acoperă:
  - **laptops**, **smartphones**, **gaming**, **audio**, **fitness**, **tablets** etc.
- Fiecare produs are:
  - `specs` (procesor, RAM, GPU, ecran, baterie etc.) folosite în indexul pentru căutare în fișe tehnice.

---

### Note / limitări

- Autentificarea este intenționat simplificată (fără JWT, parole în clar) – **doar pentru scopuri de demo / laborator**.
- Dacă variabilele Supabase nu sunt setate, aplicația funcționează exclusiv cu date in‑memory.
- Motorul IR este implementat manual pentru transparență didactică; nu este optimizat pentru colecții foarte mari, dar este suficient pentru demo și explicații despre TF‑IDF / BM25 / cosine similarity.

---

### Idei de extindere

- JWT / OAuth2 pentru autentificare reală.
- Filtre suplimentare (preț, brand, specificații tehnice) peste rezultatele IR.
- Logare de interogări și recomandări pentru analiză offline.
- Containere Docker pentru rulare rapidă end‑to‑end.
