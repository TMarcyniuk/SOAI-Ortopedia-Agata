# SOAI · Sistema de Organización y Administración de Inventario

MVP simple del inventario de **Ortopedia Agata** (proyecto de Ingeniería de Requerimientos).
Es una web interna para ver el inventario, buscar productos y cargar datos sin usar el Excel.

> Estado: **Paso 1 (productos)**. La página Productos funciona completa; Cargar datos y Dashboard todavía están vacías.

## Qué necesitás instalado
- Python 3.11 o superior
- Node.js 20 o superior
- MySQL **8.0.16 o superior** (antes de esa versión los `CHECK` de la base se ignoran).
  Para ver la versión: `SELECT VERSION();`

## 1. Base de datos (una sola vez)
Abrí MySQL (por ejemplo `mysql -u root -p`) y creá la base:

```sql
CREATE DATABASE soai CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

## 2. Backend (Flask)
Desde la carpeta `backend`, en PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Si PowerShell no deja activar el entorno, correr `Set-ExecutionPolicy -Scope Process Bypass` y probar de nuevo
(o usar `venv\Scripts\activate.bat` desde CMD).

Editá `.env` y poné tu usuario y clave de MySQL en `DATABASE_URL`
(si la clave tiene caracteres especiales como `@` o `#`, hay que codificarlos: `@` es `%40`, `#` es `%23`).

Crear las tablas y cargar las categorías:

```powershell
flask db upgrade
flask seed-categories
flask seed-demo
flask run
```

`flask seed-demo` carga 30 productos de ejemplo para poder probar (se puede correr más de una vez sin duplicar).

El backend queda en http://localhost:5000. Probá http://localhost:5000/api/health: debe mostrar `"status": "ok"`.

> La carpeta `backend/migrations/` ya viene con la migración inicial: no hace falta `flask db init`.
> Cuando cambien los modelos: `flask db migrate -m "descripción"` y después `flask db upgrade`.

## 3. Frontend (React + Vite)
En otra terminal, desde la carpeta `frontend`:

```powershell
npm install
copy .env.example .env
npm run dev
```

Abrí http://localhost:5173. Abajo a la izquierda del menú tiene que decir **"Servidor conectado"**.

En **Productos** vas a poder buscar (por código o nombre), filtrar por categoría, stock y estado, editar un producto y desactivarlo o reactivarlo.

## API disponible (Paso 1)
| Método y ruta | Para qué sirve |
|---|---|
| `GET /api/health` | Chequea servidor y base de datos |
| `GET /api/categories` | Categorías activas |
| `GET /api/products` | Lista. Parámetros: `q`, `category_id`, `stock` (`all`/`low`/`out`), `active` (`1`/`0`/`all`), `page`, `per_page` |
| `PUT /api/products/<id>` | Edita un producto (el código no se puede cambiar) |
| `POST /api/products/<id>/toggle-active` | Baja lógica: desactiva o reactiva |

Los errores siempre vienen como `{"error": "mensaje", "fields": {"campo": "detalle"}}`.

## Variables de entorno
| Archivo | Variable | Para qué sirve |
|---|---|---|
| `backend/.env` | `DATABASE_URL` | Conexión a MySQL (`mysql+pymysql://usuario:clave@localhost:3306/soai`) |
| `backend/.env` | `FLASK_APP` | Le dice a `flask` cuál es la app (`app.py`) |
| `backend/.env` | `CORS_ORIGINS` | Direcciones desde las que se puede abrir el frontend |
| `frontend/.env` | `VITE_API_URL` | Dirección del backend (`http://localhost:5000`) |

Los archivos `.env` tienen claves: **no se suben a GitHub**.

## Pasos del MVP
- [x] Paso 0: esqueleto
- [x] Paso 1: productos (lista, búsqueda, filtros, edición, baja lógica)
- [ ] Paso 2: cargar datos (manual y desde Excel/CSV)
- [ ] Paso 3: dashboard
- [ ] Paso 4: cierre
