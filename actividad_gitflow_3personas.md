# Actividad: Gitflow + Commits Semánticos + Versionamiento
## Proyecto: `orders-api` — Python / FastAPI
### Equipo: 3 personas

---

> [!IMPORTANT]
> El proyecto Python ya está funcionando. Esta actividad solo cubre el flujo de trabajo Git. Todos trabajan sobre el mismo repositorio en GitHub.

---

## Roles

| Persona | Rol | Responsabilidad |
|---|---|---|
| **Persona 1** | 🧑‍💼 Líder / DevOps | Crea el repo, configura ramas, hace releases y tags |
| **Persona 2** | 👨‍💻 Dev Backend | Trabaja en features de código Python |
| **Persona 3** | 📝 Dev Documentación | Trabaja en README, comentarios y docs |

---

## FASE 1 — Persona 1: Configurar el repositorio (30 min)

### Paso 1.1 — Crear repo en GitHub
1. Ir a [github.com](https://github.com) → **New repository**
2. Nombre: `orders-api`
3. Visibilidad: **Private** o Public
4. **NO** marcar "Add README" (ya tenemos uno)
5. Click en **Create repository**

### Paso 1.2 — Inicializar Git local
```powershell
cd c:\orders-api-develop

git init
git add .
git commit -m "chore: initial project setup with FastAPI + Uvicorn"
```

### Paso 1.3 — Conectar con GitHub y subir a `main`
```powershell
git remote add origin https://github.com/TU_USUARIO/orders-api.git
git branch -M main
git push -u origin main
```

### Paso 1.4 — Crear rama `develop` (rama de integración)
```powershell
git checkout -b develop
git push -u origin develop
```

> [!NOTE]
> `main` = código estable/producción. `develop` = integración de features. **Nunca** se trabaja directo en `main`.

### Paso 1.5 — Configurar rama por defecto
En GitHub → Settings → Branches → Default branch → cambiar a `develop`

### Paso 1.6 — Dar acceso al equipo
GitHub → Settings → Collaborators → Agregar a Persona 2 y Persona 3

---

## FASE 2 — Persona 2 y Persona 3: Clonar y configurar (15 min cada uno)

```powershell
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/orders-api.git
cd orders-api

# Crear y activar el ambiente virtual
python -m venv env
.\env\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Pararse en develop (rama base de trabajo)
git checkout develop
```

---

## FASE 3 — Persona 2: Feature de código (45 min)

### Paso 3.1 — Crear rama feature
```powershell
git checkout develop
git pull origin develop                      # siempre actualizar antes
git checkout -b feature/add-customers-endpoint
```

### Paso 3.2 — Hacer cambios en el código
Ejemplo: agregar endpoint GET /customers en `app/routes/order_routes.py`:

```python
@router.get("/customers", response_model=list[Customer], summary="Listar clientes")
def get_all_customers():
    return order_service.repo.find_all_customers()
```

### Paso 3.3 — Commit semántico
```powershell
git add app/routes/order_routes.py
git commit -m "feat(customers): add GET /api/v1/customers endpoint"
```

### Paso 3.4 — Subir la rama y crear Pull Request
```powershell
git push origin feature/add-customers-endpoint
```
Luego en GitHub: **Compare & pull request** → base: `develop` → Create PR

---

## FASE 4 — Persona 3: Feature de documentación (45 min)

### Paso 4.1 — Crear rama feature
```powershell
git checkout develop
git pull origin develop
git checkout -b feature/improve-readme
```

### Paso 4.2 — Editar README.md o agregar comentarios al código

### Paso 4.3 — Commit semántico
```powershell
git add README.md
git commit -m "docs: update README with full endpoint table and examples"
```

### Paso 4.4 — Subir y crear Pull Request
```powershell
git push origin feature/improve-readme
```
GitHub: **Compare & pull request** → base: `develop` → Create PR

---

## FASE 5 — Persona 1: Revisar y mergear PRs (20 min)

### Paso 5.1 — Revisar cada Pull Request en GitHub
- Leer los cambios en la pestaña **Files changed**
- Si está bien → **Merge pull request** → **Confirm merge**
- Si hay problemas → solicitar cambios con comentarios

### Paso 5.2 — Actualizar develop local
```powershell
git checkout develop
git pull origin develop
```

---

## FASE 6 — Persona 1: Release y tag de versión (20 min)

### Paso 6.1 — Crear rama release
```powershell
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0
```

### Paso 6.2 — Ajustes finales de la versión
Actualizar el número de versión en `main.py`:
```python
app = FastAPI(
    title="Orders API",
    version="1.0.0",   # ← confirmar que dice 1.0.0
    ...
)
```

```powershell
git add main.py
git commit -m "chore(release): bump version to 1.0.0"
```

### Paso 6.3 — Mergear release → main
```powershell
git checkout main
git merge release/v1.0.0
git push origin main
```

### Paso 6.4 — Crear el TAG de versión (Versionamiento Semántico)
```powershell
git tag -a v1.0.0 -m "release: version 1.0.0 - Orders API FastAPI inicial"
git push origin v1.0.0
```

### Paso 6.5 — Mergear release → develop (para sincronizar)
```powershell
git checkout develop
git merge release/v1.0.0
git push origin develop
```

### Paso 6.6 — Eliminar la rama release
```powershell
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

---

## Referencia: Commits Semánticos

Formato: `tipo(alcance): descripción corta`

| Tipo | Cuándo usarlo | Ejemplo |
|---|---|---|
| `feat` | Nueva funcionalidad | `feat(orders): add PATCH /orders endpoint` |
| `fix` | Corrección de bug | `fix(service): correct totalAmount calculation` |
| `docs` | Solo documentación | `docs: add usage examples to README` |
| `chore` | Tareas de configuración | `chore: add python-dotenv to requirements` |
| `refactor` | Mejora sin cambiar funcionalidad | `refactor(repo): simplify find_order_by_id` |
| `test` | Añadir/modificar tests | `test: add unit test for order service` |
| `style` | Formato, espacios (sin lógica) | `style: fix indentation in order_routes.py` |

---

## Referencia: Versionamiento Semántico (SemVer)

Formato: `MAYOR.MENOR.PARCHE` → ejemplo `v1.0.0`

| Número | Cuándo aumenta | Ejemplo |
|---|---|---|
| **MAYOR** (1) | Cambio que rompe compatibilidad | `v1.0.0 → v2.0.0` |
| **MENOR** (0) | Nueva funcionalidad compatible | `v1.0.0 → v1.1.0` |
| **PARCHE** (0) | Corrección de bug | `v1.0.0 → v1.0.1` |

---

## Referencia: Estructura de ramas Gitflow

```
main          ←── producción estable, solo recibe merges de release
  │
develop       ←── integración, recibe merges de features
  │
  ├── feature/add-customers-endpoint   ← Persona 2
  ├── feature/improve-readme           ← Persona 3
  └── release/v1.0.0                  ← Persona 1 (al liberar)
```

---

## Checklist final por persona

### Persona 1 ✅
- [ ] Repo creado en GitHub
- [ ] Ramas `main` y `develop` configuradas
- [ ] PRs revisados y mergeados
- [ ] Tag `v1.0.0` creado y subido
- [ ] Release mergeada a `main` y `develop`

### Persona 2 ✅
- [ ] Rama `feature/` creada desde `develop`
- [ ] Cambios de código con commit semántico `feat:`
- [ ] PR creado hacia `develop`

### Persona 3 ✅
- [ ] Rama `feature/` creada desde `develop`
- [ ] Cambios de docs con commit semántico `docs:`
- [ ] PR creado hacia `develop`
