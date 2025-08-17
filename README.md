# DSND Dashboard Project

Dashboard de desempeño para **empleados** y **equipos** usando **FastHTML**, **SQLite** y un modelo de **ML** (`assets/model.pkl`) para estimar riesgo de reclutamiento.

## Requisitos
- Python 3.11 recomendado
- SQLite (incluido con Python)
- Windows, macOS o Linux

## Instalación rápida

### 1) Crear y activar entorno virtual
**Windows PowerShell**
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```
python -m venv .venv
source .venv/bin/activate
```

### 2) Instalar dependencias
```
python -m pip install -U pip
pip install -r requirements.txt
```

### 3) Instalar el paquete local en modo editable
```
python -m pip install -e python-package
```

## Ejecutar el dashboard
```
python report/dashboard.py
```
Abre la URL que imprime (por ejemplo, `http://localhost:5001`).

Desde la UI puedes alternar entre **Employee** y **Team**, elegir la entidad en el **dropdown** y ver:
- **Eventos acumulados** (línea): positivos vs. negativos.
- **Predicted Recruitment Risk** (barra): probabilidad estimada.
- **Notas** (tabla): últimas anotaciones para el empleado/equipo.

## Rutas útiles
- `/` → Página principal
- `/employee/{id}` → Reporte de empleado por ID (ej. `/employee/1`)
- `/team/{id}` → Reporte de equipo por ID (ej. `/team/1`)

> Nota: el selector envía el **ID** de la entidad; si por alguna razón la ruta recibe un **nombre**, el backend lo mapea al ID correspondiente.

## Pruebas
```
pytest -q
```
Incluye verificaciones de existencia de la base y tablas principales.

## Estructura del repositorio (resumen)
```
.
├── README.md
├── assets
│   ├── model.pkl
│   └── report.css
├── python-package
│   ├── employee_events
│   │   ├── __init__.py
│   │   ├── employee.py
│   │   ├── employee_events.db
│   │   ├── query_base.py
│   │   ├── sql_execution.py
│   │   └── team.py
│   ├── requirements.txt
│   └── setup.py
├── report
│   ├── base_components
│   │   ├── __init__.py
│   │   ├── base_component.py
│   │   ├── data_table.py
│   │   ├── dropdown.py
│   │   ├── matplotlib_viz.py
│   │   └── radio.py
│   ├── combined_components
│   │   ├── __init__.py
│   │   ├── combined_component.py
│   │   └── form_group.py
│   ├── dashboard.py
│   └── utils.py
├── requirements.txt
├── tests
│   └── test_employee_events.py
└── .gitignore
```

## Modelo de datos (ER)
*Mermaid (puedes pegar esto en https://mermaid.live para visualizar):*
```
erDiagram

  employee {
    INTEGER employee_id PK
    TEXT first_name
    TEXT last_name
    INTEGER team_id
  }

  team {
    INTEGER team_id PK
    TEXT team_name
    TEXT shift
    TEXT manager_name
  }

  employee_events {
    TEXT event_date
    INTEGER employee_id FK
    INTEGER team_id FK
    INTEGER positive_events
    INTEGER negative_events
  }

  notes {
    INTEGER employee_id PK
    INTEGER team_id PK
    TEXT note
    TEXT note_date PK
  }

  team ||--o{ employee : "team_id"
  team ||--o{ employee_events : "team_id"
  employee ||--o{ employee_events : "employee_id"
  employee ||--o{ notes : "employee_id"
  team ||--o{ notes : "team_id"
```

## ¿Qué hace cada módulo?

- **python-package/employee_events/sql_execution.py**  
  Mixin `QueryMixin` (métodos `pandas_query`/`query`) y decorador `@query` para ejecutar SQL con SQLite.

- **employee_events/query_base.py**  
  Métodos base para consultar eventos diarios y notas (usando el mixin).

- **employee_events/employee.py** y **employee_events/team.py**  
  Subclases que implementan `names`, `username`, `model_data`, etc.

- **report/utils.py**  
  `load_model()` con `pathlib` para resolver `assets/model.pkl`.

- **report/dashboard.py**  
  Componentes heredados: `ReportDropdown`, `Header`, `LineChart`, `BarChart`, `NotesTable`, `Visualizations`, `Report`.  
  Rutas `/`, `/employee/{id}`, `/team/{id}`.

## Troubleshooting

1) **ModuleNotFoundError: No module named "employee_events"**  
   Instala el paquete en editable:
   ```
   python -m pip install -e python-package
   ```

2) **ModuleNotFoundError: No module named "sqlite_minutils"** al importar `fasthtml.common`  
   Instala la dependencia usada por FastHTML:
   ```
   pip install sqlite-minutils
   ```

3) **Al cambiar de empleado, la URL lleva un nombre y falla (`ValueError: invalid literal for int()`)**  
   El dropdown debe enviar IDs. En este repo ya se maneja y, además, el backend traduce nombres → IDs.

4) **PowerShell bloquea el activador del venv**  
   Ejecuta:
   ```
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

## Notas
- `model.pkl` es un modelo de clasificación; si no tiene `predict_proba`, se aplica un fallback seguro.
- Rutas y consultas usan `pathlib` y SQL para SQLite.
