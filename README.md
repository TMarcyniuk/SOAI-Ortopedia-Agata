# SOAI — Sistema de Organización y Administración de Inventario

SOAI es una aplicación web desarrollada con Flask (Python), React y MySQL para **Ortopedia Agata**. Reemplaza la planilla de Excel: permite buscar productos y consultar su precio y stock, editarlos y darlos de baja, administrar categorías, y cargar productos nuevos a mano o importándolos desde un archivo Excel o CSV.

El proyecto tiene tres partes que se ejecutan en tu computadora: la **base de datos** (MySQL), el **backend** (Flask, carpeta `backend`) y el **frontend** (React, carpeta `frontend`). La base de datos viene en un archivo `.sql` que se importa una sola vez.

## Requisitos previos
Antes de ejecutar el proyecto, instalá:

* **Python 3.11 o superior**: https://www.python.org/downloads/ . En Windows, durante la instalación marcá la opción *Add Python to PATH*.
* **Node.js 20 o superior**: https://nodejs.org/
* **MySQL Server 8.0.16 o superior**: https://dev.mysql.com/downloads/mysql/ . Durante la instalación se te pide crear una **contraseña para el usuario `root`**: anotala, la vas a necesitar.
* **MySQL Workbench**: https://dev.mysql.com/downloads/workbench/
* **Visual Studio Code** (opcional, recomendado para editar archivos): https://code.visualstudio.com/

## Instalación y configuración

### 1. Abrir el proyecto
Abrí en Visual Studio Code la carpeta `soai` (la que contiene las carpetas `backend` y `frontend`). 

### 2. Importar la base de datos
Asegurate de que MySQL Server esté iniciado.

1. Abrí **MySQL Workbench**.
2. Hacé doble clic en tu conexión local (normalmente se llama *Local instance MySQL80*) e ingresá la contraseña del usuario `root`.
3. Andá a *File > Open SQL Script* y elegí el archivo `soai_dump.sql`.
4. Hacé clic en el ícono del **rayo** (*Execute*) de la barra superior y esperá a que termine.
5. Para comprobar que se importó, en el panel izquierdo (*Schemas*) hacé clic en el botón de actualizar. Tiene que aparecer la base **`soai`** con sus tablas (`categories` y `products`).

Importante: el archivo crea la base `soai` y reemplaza sus tablas. Si ya tenías una base con ese nombre y querés conservar su información, hacé una copia de seguridad antes de importar. No hace falta crear nada más ni ejecutar migraciones.

### 3. Preparar el backend
Cre una terminal (CMD o Powershell) y entrá a la carpeta `backend`:

```
cd C: (ruta absoluta)
```

Creá y activá un entorno virtual (mantiene separadas las dependencias del proyecto).

Windows (PowerShell):

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS o Linux:

```
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno esté activo, vas a ver `(venv)` al comienzo de la línea de la terminal. Con el entorno activado, instalá las dependencias:

```
pip install -r requirements.txt
```

### 4. Configurar la conexión a MySQL
Abrí el archivo `backend\.env` (en Visual Studio Code: panel izquierdo, carpeta `backend`, archivo `.env`). Vas a ver esta línea:

```
DATABASE_URL=mysql+pymysql://usuario:clave@localhost:3306/soai
```

Tenés que reemplazar **`usuario`** y **`clave`** por tus datos de MySQL, sin dejar espacios ni comillas:

| Parte | Qué poner |
|---|---|
| `usuario` | El usuario de MySQL con el que entrás a MySQL Workbench. Si no creaste otro, es `root`. |
| `clave` | La contraseña de ese usuario. Es la que creaste al instalar MySQL Server. |
| `localhost:3306` | No se cambia (es la dirección y el puerto normales de MySQL). |
| `soai` | No se cambia (es el nombre de la base que importaste en el paso 2). |

Ejemplo: si tu usuario es `root` y tu contraseña es `Mi.Clave1`, la línea queda así:

```
DATABASE_URL=mysql+pymysql://root:Mi.Clave1@localhost:3306/soai
```

Si no estás seguro de tu contraseña, probala en MySQL Workbench: si te deja entrar a la conexión local, es la correcta.

**Contraseñas con caracteres especiales.** Si tu contraseña tiene alguno de estos caracteres, escribilo con su código:

| Carácter | Se escribe |
|---|---|
| `@` | `%40` |
| `#` | `%23` |
| `/` | `%2F` |
| `:` | `%3A` |
| `%` | `%25` |
| espacio | `%20` |

Por ejemplo, la contraseña `Clave@2026` se escribe `Clave%402026`:

```
DATABASE_URL=mysql+pymysql://root:Clave%402026@localhost:3306/soai
```

No modifiques las demás líneas del archivo. Guardá los cambios. Este archivo contiene tu contraseña, así que no lo compartas.

### 5. Ejecutar el backend
Con el entorno virtual activado y la terminal ubicada en la carpeta `backend`, ejecutá:

```
flask run
```

Para comprobar que funciona, abrí en el navegador http://localhost:5000/api/health . Tiene que mostrar `"status": "ok"`. **Dejá esta terminal abierta**: si la cerrás, el sistema deja de funcionar.

### 6. Preparar y ejecutar el frontend
Abrí una **segunda terminal** en Visual Studio Code (sin cerrar la anterior), posicionate sobre la carpeta `frontend` y ejecutá:


```
npm install
npm run dev
```

No hace falta modificar `frontend\.env`. **Dejá esta terminal abierta también.**

### 7. Abrir SOAI
Abrí el navegador e ingresá a:

http://localhost:5173

Abajo a la izquierda del menú tiene que decir **"Servidor conectado"**. Ya podés usar las dos secciones del sistema:

* **Productos**: buscar, filtrar, editar y desactivar productos.
* **Cargar datos**: agregar un producto a mano, administrar categorías o importar muchos productos desde un Excel (con el botón *Descargar plantilla* obtenés el formato).

Para cerrar el sistema, presioná `Ctrl + C` en las dos terminales.

### Para volver a usarlo otro día
No hace falta repetir la instalación. Abrí dos terminales:

* En la primera, desde la carpeta `backend`: activá el entorno virtual (`.\venv\Scripts\Activate.ps1`) y ejecutá `flask run`.
* En la segunda, desde la carpeta `frontend`: ejecutá `npm run dev`.

Después abrí http://localhost:5173 .

## Solución de problemas

* **`Access denied for user` o error de conexión al iniciar el backend:** el usuario o la contraseña de `backend\.env` no coinciden con los de tu MySQL. Revisá el paso 4, en especial los caracteres especiales de la contraseña.
* **`Unknown database 'soai'`:** la base no está importada. Repetí el paso 2.
* **`WinError 10061` o no se puede conectar a MySQL:** el servicio de MySQL está apagado. Abrí PowerShell **como administrador** y ejecutá `net start MySQL80`.
* **El menú dice "Sin conexión con el servidor":** el backend no está en ejecución. Revisá que la primera terminal siga abierta con `flask run` funcionando.
* **`flask` no se reconoce como comando:** el entorno virtual no está activado. Activalo como se indica en el paso 3.
* **PowerShell no permite activar el entorno virtual:** ejecutá `Set-ExecutionPolicy -Scope Process Bypass` y volvé a probar.
* **Error `Unknown collation: utf8mb4_0900_ai_ci` al importar:** estás usando MariaDB o una versión de MySQL anterior a la 8.0. Instalá MySQL Server 8.0.16 o superior.
* **Un puerto está ocupado (5000 o 5173):** cerrá la otra aplicación que lo esté usando antes de volver a iniciar.
