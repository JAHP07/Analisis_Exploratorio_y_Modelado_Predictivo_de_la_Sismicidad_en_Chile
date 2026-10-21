# 🌋 Análisis Exploratorio y Modelado Predictivo de la Sismicidad en Chile

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/JAHP07/Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile/actions/workflows/ci.yml/badge.svg)](https://github.com/JAHP07/Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile/actions/workflows/ci.yml)

> **ES**: Proyecto open source para extraer, limpiar, analizar y visualizar sismicidad observada en Chile usando datos públicos de USGS.
>
> **EN**: Open-source project to extract, clean, analyze, and visualize observed seismicity in Chile using public USGS data.

---

## 1) Objetivo del proyecto / Project goal

**ES**
- Implementar un pipeline reproducible de análisis sísmico (ETL + EDA + modelado exploratorio + visualización).
- Facilitar aprendizaje práctico en ciencia de datos, calidad de código y colaboración open source.
- Entregar resultados transparentes y trazables con documentación clara.

**EN**
- Provide a reproducible seismic analysis pipeline (ETL + EDA + exploratory modeling + visualization).
- Support practical learning in data science, code quality, and open-source collaboration.
- Deliver transparent, traceable outputs with clear documentation.

---

## 2) Alcance científico y limitaciones / Scientific scope and limitations

**ES**
- Este repositorio analiza **sismicidad histórica observada**, no predice terremotos de forma determinista.
- Los modelos de regresión y clustering se usan con fines exploratorios.
- La calidad de resultados depende de la cobertura y calidad de datos reportados por fuentes oficiales.

**EN**
- This repository analyzes **historical observed seismicity**; it is not an earthquake prediction system.
- Regression and clustering are exploratory tools.
- Result quality depends on official-source data quality and coverage.

---

## 3) Arquitectura técnica / Technical architecture

```text
USGS API (GeoJSON)
   │
   ├─ src/extraccion_datos.py
   │    ├─ obtener_datos_sismos()
   │    └─ limpiar_datos_sismos()
   │
   ├─ src/analisis.py
   │    ├─ estadistica_descriptiva()
   │    ├─ analizar_relacion_magnitud_profundidad()
   │    ├─ agrupar_sismos()
   │    └─ generar_resumen_kpi()
   │
   ├─ src/visualizacion.py
   │    ├─ graficar_distribucion_magnitud()
   │    ├─ graficar_profundidad_vs_magnitud()
   │    ├─ graficar_distribucion_geografica()
   │    └─ generar_todas_visualizaciones()
   │
   └─ output/*.png
```

---

## 4) Tecnologías / Stack

- Python 3.12
- pandas, NumPy
- scikit-learn
- matplotlib, seaborn
- pytest
- Ruff
- GitHub Actions + Dev Containers/Codespaces

---

## 5) Estructura del repositorio / Repository layout

```text
.
├── src/
├── tests/
├── notebooks/
├── output/
├── .github/workflows/ci.yml
├── .devcontainer/devcontainer.json
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 6) Instalación local (ES)

```bash
git clone https://github.com/JAHP07/Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile.git
cd Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 7) Local setup (EN)

```bash
git clone https://github.com/JAHP07/Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile.git
cd Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 8) Uso rápido / Quick usage

```python
from src.extraccion_datos import obtener_datos_sismos, limpiar_datos_sismos
from src.analisis import generar_resumen_kpi
from src.visualizacion import generar_todas_visualizaciones

df = obtener_datos_sismos(fecha_inicio="2025-01-01", fecha_fin="2025-12-31", magnitud_minima=4.0)
df = limpiar_datos_sismos(df)
print(generar_resumen_kpi(df))
print(generar_todas_visualizaciones(df, output_dir="output"))
```

---

## 9) Notebooks

- Notebook principal: [`notebooks/analisis_sismico.ipynb`](notebooks/analisis_sismico.ipynb)
- Colab: <https://colab.research.google.com/github/JAHP07/Analisis_Exploratorio_y_Modelado_Predictivo_de_la_Sismicidad_en_Chile/blob/main/notebooks/analisis_sismico.ipynb>

---

## 10) Visualizaciones existentes

- ![Distribución de Magnitudes](output/magnitude_distribution.png)
- ![Profundidad vs Magnitud](output/depth_vs_magnitude.png)
- ![Distribución Geográfica](output/geographic_distribution.png)

---

## 11) Pruebas y calidad / Testing and quality

```bash
ruff check .
ruff format --check .
pytest -v
```

CI ejecuta estas verificaciones en pushes y pull requests hacia `main`.

---

## 12) GitHub Codespaces

El repositorio incluye `.devcontainer/devcontainer.json` compatible con Python 3.12.
Al abrir un Codespace, se instala automáticamente `requirements.txt`.

---

## 13) Contribuciones / Contributing

Consulta:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [Plantilla de PR](.github/pull_request_template.md)

Etiquetas sugeridas para colaboración:
- `good first issue`
- `help wanted`
- `bug`
- `documentation`

---

## 14) Fuentes de datos oficiales / Official data sources

- USGS Earthquake Catalog API: <https://earthquake.usgs.gov/fdsnws/event/1/>

---

## 15) Uso responsable de IA / Responsible AI use

Este proyecto puede usar asistencia de IA para tareas de apoyo en código y documentación.
Todo cambio debe ser revisado por personas antes de aprobarse y fusionarse.

---

## 16) Licencia y créditos / License and credits

- Licencia: [MIT](LICENSE)
- Autor: [JAHP07](https://github.com/JAHP07)
