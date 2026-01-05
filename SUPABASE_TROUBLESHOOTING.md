# Troubleshooting Supabase - Datele nu se actualizează

## Problema
Site-ul funcționează dar datele nu se salvează în Supabase.

## Cauze posibile și soluții

### 1. Row Level Security (RLS) - CEA MAI COMUNĂ CAUZĂ

**Problema:** RLS policies blochează operațiunile de scriere când folosești `anon key`.

**Soluții:**

#### Opțiunea A: Folosește Service Role Key (RECOMANDAT pentru backend)

1. În Supabase Dashboard → Settings → API
2. Copiază **service_role key** (NU anon key!)
3. În `backend/.env`, folosește:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```
4. Service Role Key bypass RLS complet - perfect pentru backend server-side
5. **IMPORTANT:** NU expune service_role key în frontend!

#### Opțiunea B: Dezactivează RLS temporar (DOAR pentru testare)

Rulează în SQL Editor:
```sql
ALTER TABLE public.products DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.favorites DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items DISABLE ROW LEVEL SECURITY;
```

#### Opțiunea C: Creează policies permissive

Rulează `SUPABASE_RLS_FIX.sql` în SQL Editor.

### 2. Verifică conexiunea

1. Verifică logs-urile serverului la pornire
2. Accesează `http://localhost:8000/api/debug/db`
3. Verifică dacă vezi `"supabase_status": "connected"`

### 3. Verifică credențialele

În `backend/.env`, asigură-te că ai:
```env
SUPABASE_URL=https://your-project.supabase.co  # Fără slash la final!
SUPABASE_KEY=your-key-here  # sau SUPABASE_SERVICE_ROLE_KEY
```

### 4. Verifică log-urile

Serverul loghează acum toate operațiunile. Verifică:
- "Attempting to insert product"
- "Successfully created product"
- "Error creating product in DB"

### 5. Test manual

Încearcă să inserezi manual în Supabase Dashboard → Table Editor pentru a verifica dacă tabelele funcționează.

### 6. Verifică schema

Asigură-te că ai rulat `supabase_schema.sql` și că tabelele există:
- products
- favorites  
- orders
- order_items

## Debugging pas cu pas

1. **Verifică conexiunea:**
   ```bash
   curl http://localhost:8000/api/debug/db
   ```
   Ar trebui să vezi `"supabase_status": "connected"`

2. **Verifică logs-urile:**
   Când adaugi un produs, ar trebui să vezi în logs:
   ```
   INFO: Attempting to insert product: ...
   INFO: Successfully created product: ...
   ```

3. **Testează direct în Supabase:**
   Încearcă să inserezi manual un produs în Table Editor pentru a verifica dacă funcționează.

4. **Verifică RLS policies:**
   În Supabase Dashboard → Authentication → Policies, verifică dacă există policies care blochează operațiunile.

## Soluție rapidă (pentru testare)

Pentru a testa rapid, rulează în SQL Editor:
```sql
-- Dezactivează RLS (DOAR pentru testare!)
ALTER TABLE public.products DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.favorites DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items DISABLE ROW LEVEL SECURITY;
```

Apoi folosește service_role key în `.env` pentru producție.

