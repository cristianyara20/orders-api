# Orders API (Backend)

## Descripción del Proyecto
Este proyecto es una API RESTful desarrollada con **Python y FastAPI** para la gestión de órdenes de venta. Proporciona una arquitectura robusta que permite crear, consultar, modificar y eliminar pedidos (`Orders`), así como administrar los items individuales de cada pedido (`Order Items`) con cálculo automático de totales. Además, expone endpoints para la consulta de productos y verificación del estado del sistema.



## Tecnologías Utilizadas
- **Python 3.14**
- **FastAPI**
- **Uvicorn** (Servidor ASGI)
- **Pydantic v2**
- **python-dotenv**

---

## Instrucciones de Instalación y Ejecución Local

Sigue los siguientes pasos para clonar, instalar y ejecutar el proyecto en tu máquina local.

### 1. Clonar el repositorio
Abre una terminal y ejecuta el siguiente comando:
```bash
git clone <https://github.com/cristianyara20/orders-api.git>
cd orders-api
```

### 2. Crear y activar un entorno virtual
Se recomienda el uso de un entorno virtual para no interferir con las dependencias globales de Python en tu sistema.

**En Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python -m venv env
source env/bin/activate
```

### 3. Instalar dependencias
Con el entorno virtual activado, instala los paquetes necesarios usando `pip`:
```bash
pip install -r requirements.txt
```

### 4. Variables de Entorno
El proyecto utiliza un archivo `.env` en la raíz (junto a `main.py`). Crea el archivo con la siguiente configuración base:
```env
PORT=3000
ENV=development
```

### 5. Ejecutar la Aplicación
Para iniciar el servidor, ejecuta el archivo principal:
```bash
python main.py
```
*(La aplicación se levantará en el puerto 3000)*

---

## Documentación de la API

FastAPI genera la documentación automáticamente. Puedes explorar e interactuar con los endpoints desde tu navegador:

- **Swagger UI (Interactiva):** [http://localhost:3000/api/v1/docs](http://localhost:3000/api/v1/docs)
- **ReDoc (Referencia):** [http://localhost:3000/api/v1/redoc](http://localhost:3000/api/v1/redoc)
- **Health Check:** [http://localhost:3000/api/v1/health](http://localhost:3000/api/v1/health)

## Estructura Principal
- **`/app/models/`**: Esquemas de Pydantic para la validación.
- **`/app/repositories/`**: Lógica de persistencia de datos (JSON/Memoria).
- **`/app/routes/`**: Controladores y endpoints de la API.
- **`/app/services/`**: Lógica de negocio (ej. cálculo de totales).

