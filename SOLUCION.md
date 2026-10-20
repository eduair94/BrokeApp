# Resolución — BrokeApp: CI/CD con GitHub Actions y Docker

**Repositorio original:** [ORT-ATI-CertificadoDevOps/BrokeApp](https://github.com/ORT-ATI-CertificadoDevOps/BrokeApp) · **Fork con la solución:** [eduair94/BrokeApp](https://github.com/eduair94/BrokeApp) · **Verificado el:** 2026-10-20

**Resultado:** con un push a `main`, el pipeline completo (`Test → Build → Validate`) termina en verde en GitHub Actions y la imagen se publica en GHCR como `ghcr.io/eduair94/brokeapp`, con las etiquetas `main` y el SHA corto del commit. Se corrigieron los 10 problemas de la consigna y se agregaron 4 mejoras en commits separados.

Para cada problema se documenta qué fallaba (con el mensaje de error real, reproducido), la causa raíz, la corrección y cómo se verificó. `app/main.py` **no se modificó**: se tomó como especificación y el resto de los archivos se alineó con él.

---

## Resumen

| # | Problema de la consigna | Archivo | Antes | Después | Commit |
|---|---|---|---|---|---|
| 1.1 | Trigger desde rama main | `ci-cd.yml` | `branches: [ dev ]` | `branches: [ main ]` | [0f02057](https://github.com/eduair94/BrokeApp/commit/0f02057) |
| 1.2 | Versión de Python incorrecta | `ci-cd.yml` | `python-version: '3.1'` | `python-version: '3.13'` | [48c44fa](https://github.com/eduair94/BrokeApp/commit/48c44fa) |
| 1.3 | Nombre del archivo de dependencias incorrecto | `ci-cd.yml` | `pip install -r requirement.txt` | `pip install -r requirements.txt` | [a9e4c67](https://github.com/eduair94/BrokeApp/commit/a9e4c67) |
| 1.4 | Directorio de tests incorrecto | `ci-cd.yml` | `python -m pytest tests/` | `python -m pytest app/` | [9eddae1](https://github.com/eduair94/BrokeApp/commit/9eddae1) |
| 2.1 | Imagen actualizada de Python | `Dockerfile` | `FROM python:2.7` | `FROM python:3.13-slim` | [0412c76](https://github.com/eduair94/BrokeApp/commit/0412c76) |
| 2.2 | Revisar ruta de copia de requirements.txt | `Dockerfile` | `COPY requirements.txt /tmp/requirements.txt` | `COPY requirements.txt .` | [9770c21](https://github.com/eduair94/BrokeApp/commit/9770c21) |
| 2.3 | Corregir error al ejecutar la aplicación | `Dockerfile` | `CMD ["python", "app.py"]` | `CMD ["python", "main.py"]` | [6290d7d](https://github.com/eduair94/BrokeApp/commit/6290d7d) |
| 3.1 | Solucionar comportamiento del test | `app/test_main.py` | `assertEqual(response.status_code, 2000)` | `assertEqual(response.status_code, 200)` | [5ba7cab](https://github.com/eduair94/BrokeApp/commit/5ba7cab) |
| 3.2 | Nombre del endpoint de check incorrecto | `app/test_main.py` | `self.app.get('/ping')` | `self.app.get('/health')` | [ea0e467](https://github.com/eduair94/BrokeApp/commit/ea0e467) |
| 3.3 | Valor de respuesta incorrecto | `app/test_main.py` | `assertEqual(data['status'], 'ok')` | `assertEqual(data['status'], 'OK')` | [9c6591e](https://github.com/eduair94/BrokeApp/commit/9c6591e) |

Mejoras adicionales, fuera del checklist (detalle en [Mejoras adicionales](#mejoras-adicionales-fuera-del-checklist)):

| # | Mejora | Archivo | Commit |
|---|---|---|---|
| E1 | El paso `Validate /ping endpoint` pasa a llamarse `Validate /health endpoint` | `ci-cd.yml` | [105d06a](https://github.com/eduair94/BrokeApp/commit/105d06a) |
| E2 | `>> $GITHUB_OUTPUT` → `>> "$GITHUB_OUTPUT"` | `ci-cd.yml` | [ea32d87](https://github.com/eduair94/BrokeApp/commit/ea32d87) |
| E3 | El contenedor corre sin root (`USER appuser`) | `Dockerfile` | [ec7642a](https://github.com/eduair94/BrokeApp/commit/ec7642a) |
| E4 | Permisos mínimos del `GITHUB_TOKEN` por job | `ci-cd.yml` | [d83b680](https://github.com/eduair94/BrokeApp/commit/d83b680) |

Ejecuciones en GitHub Actions (fork):

| Run | Código | Test | Build | Validate |
|---|---|---|---|---|
| [39513506166](https://github.com/eduair94/BrokeApp/actions/runs/39513506166) | Solo los 10 fixes del checklist (`9c6591e`) | ✅ 10 s | ✅ 23 s | ✅ 16 s |
| [39514055326](https://github.com/eduair94/BrokeApp/actions/runs/39514055326) | Checklist + mejoras E1–E4 (`d83b680`) | ✅ 10 s | ✅ 39 s | ✅ 10 s |

El primer run muestra que los 10 fixes del checklist alcanzan para que el pipeline funcione; el segundo, que las mejoras no rompen nada. Los runs posteriores, incluido el del commit de este documento, están en la [pestaña Actions](https://github.com/eduair94/BrokeApp/actions/workflows/ci-cd.yml).

---

## Metodología

1. **Reproducir antes de corregir.** Cada falla se reprodujo localmente con Docker, ejecutando los mismos comandos del workflow sobre el contenido exacto del commit (`git archive`). Los mensajes de error citados abajo son los que se obtuvieron así.
2. **Un cambio por commit, verificando cada uno.** Varios errores estaban **encadenados**: uno ocultaba al siguiente (ver [Docker](#2-docker--dockerfile) y [APP / Testing](#3-app--testing--apptest_mainpy)). Corrigiendo de a uno se puede demostrar que cada cambio era necesario.
3. **Simulación local del workflow.** Un script auxiliar (no incluido en el repo) leyó el YAML de cada commit, ejecutó los pasos `run:` del job `test` en un contenedor `python:<versión>-slim` (con la versión tomada del propio YAML), construyó la imagen (`build`) y corrió los pasos del job `validate` contra el contenedor. Workflow original: 4 fallas. Con los fixes: 12/12 chequeos OK.
4. **Lint del workflow** con [actionlint](https://github.com/rhysd/actionlint) 1.7.12, que incluye shellcheck.
5. **Ejecución real** en GitHub Actions, en el fork (tabla de arriba).

---

## 1. Integración Continua — `.github/workflows/ci-cd.yml`

### 1.1 Trigger desde rama `main`

**Problema.** El workflow solo se disparaba con push a `dev`:

```yaml
on:
  push:
    branches: [ dev ]      # la rama dev no existe en el repositorio
  pull_request:
    branches: [ main ]
```

Un push a `main` no ejecutaba nada. El único evento que alcanzaba a `main` era `pull_request`, pero en ese evento el workflow **no publica la imagen** (`push: ${{ github.event_name != 'pull_request' }}`) y **saltea el job `validate`** (`if: github.event_name != 'pull_request'`). Con la configuración original, la imagen nunca se publicaba ni se validaba.

**Corrección.**

```diff
   push:
-    branches: [ dev ]
+    branches: [ main ]
```

**Verificación.** Los pushes a `main` del fork dispararon el workflow (evento `push`, rama `main`): ver los runs del resumen.

### 1.2 Versión de Python incorrecta

**Problema.** `python-version: '3.1'` pide CPython **3.1**, de 2009 (no 3.10). `actions/setup-python` busca la versión primero en la caché del runner y después en su [manifest de versiones](https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json). Ahí la única 3.1.x es la 3.1.4, y **solo para Windows**, así que en `ubuntu-latest` el paso falla. Según el código de setup-python v6 (`src/find-python.ts`), el mensaje es:

```
The version '3.1' with architecture 'x64' was not found for Ubuntu 24.04.
The list of all available versions can be found here: https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json
```

Aunque existiera, Python 3.1 no podría instalar Flask 2.0.3, que requiere Python ≥ 3.6.

**Por qué 3.13.** Se probaron las dependencias fijadas en `requirements.txt` (Flask 2.0.3, Werkzeug 2.0.3, pytest 6.2.5) contra cada versión de Python, en contenedores `python:<versión>-slim` y con los tests ya corregidos:

| Python | Soporte hasta | `pytest app/` | `python main.py` |
|---|---|---|---|
| 3.10 | 2026-10-01 (**ya sin soporte**) | ✅ 2 passed | ✅ responde |
| 3.11 | 2027-10-31 | ✅ 2 passed | ✅ responde |
| 3.12 | 2028-10-31 | ✅ 2 passed, 65 warnings | ✅ responde |
| **3.13** | **2029-10-31** | ✅ **2 passed, 89 warnings** | ✅ **responde** |
| 3.14 | 2030-10-31 | ❌ `AttributeError: module 'ast' has no attribute 'Str'` | ❌ `AttributeError: module 'pkgutil' has no attribute 'get_loader'` |
| 3.15 | 2031-10-31 | ❌ mismo error | ❌ mismo error |

- **3.13 es la versión más nueva que funciona** con estas dependencias, y tiene soporte hasta octubre de 2029.
- Python 3.14 eliminó `ast.Str`, que Werkzeug 2.0.3 usa para compilar las rutas, y `pkgutil.get_loader`, que Flask 2.0.3 usa al crear la app. Para usar 3.14 o superior hay que actualizar Flask y Werkzeug (ver [Observaciones](#observaciones-y-recomendaciones-no-aplicadas)).
- Los *warnings* de 3.12 y 3.13 no vienen del código del repo. Son `DeprecationWarning` emitidos **dentro de Werkzeug 2.0.3** (`ast.Str is deprecated and will be removed in Python 3.14`) y un `RuntimeWarning` de unittest (`TestResult has no addDuration method`), por usar pytest 6.2.5 con Python ≥ 3.12. No afectan el resultado.
- Es **la misma versión que la imagen Docker** (ver 2.1): los tests corren sobre el mismo runtime que se publica.
- El manifest publica 3.13 para Ubuntu 22.04, 24.04 y **26.04**, así que la versión sigue disponible cuando `ubuntu-latest` migre a Ubuntu 26, como anuncian las anotaciones de los runs.

**Corrección.**

```diff
-        python-version: '3.1'
+        python-version: '3.13'
```

La versión va **entre comillas**: en YAML, `3.10` sin comillas se lee como el número `3.1`. Conviene escribir siempre las versiones como string.

**Verificación.** Log del job Test: `Successfully set up CPython (3.13.16)`.

### 1.3 Nombre del archivo de dependencias incorrecto

**Problema.** Faltaba la "s":

```
$ pip install -r requirement.txt
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirement.txt'
```

**Corrección.** `pip install -r requirements.txt`.

**Verificación.** El job instala `Flask-2.0.3 … Werkzeug-2.0.3 … pytest-6.2.5`.

### 1.4 Directorio de tests incorrecto

**Problema.** El directorio `tests/` no existe; el único archivo de tests es `app/test_main.py`:

```
$ python -m pytest tests/
ERROR: file or directory not found: tests/
```

pytest termina con código 4 (error de uso).

**Corrección.** `python -m pytest app/`.

**Por qué funciona el import.** `test_main.py` hace `from main import app`. Como `app/` no tiene `__init__.py`, pytest (con su modo de importación por defecto, `prepend`) agrega `app/` al principio de `sys.path` antes de importar el test, y `main` resuelve a `app/main.py`. No hace falta `cd app` ni definir `PYTHONPATH`.

**Verificación.** Log del job Test: `2 passed, 89 warnings`.

---

## 2. Docker — `Dockerfile`

Los tres errores estaban encadenados. El build original solo mostraba el de la ruta (2.2), que ocultaba el de la versión (2.1). El de `CMD` (2.3) aparece recién al ejecutar el contenedor, cuando el build ya funciona:

| Estado del Dockerfile | Resultado |
|---|---|
| Original | ❌ build: `ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'` |
| Solo 2.2 corregido (sigue `python:2.7`) | ❌ build: `ERROR: No matching distribution found for Flask==2.0.3` |
| Solo 2.1 corregido | ❌ build: el mismo error de ruta que el original |
| 2.1 + 2.2 | ✅ build · ❌ el contenedor termina con código 2: `python: can't open file '/app/app.py'` |
| 2.1 + 2.2 + 2.3 | ✅ `GET /health` → `{"status":"OK"}` y `GET /` → `{"message": …}`, ambos HTTP 200 |

### 2.1 Imagen actualizada de Python

**Problema.** `FROM python:2.7`. Python 2.7 no tiene soporte desde el 2020-01-01. Además, Flask 2.x declara `Requires-Python >=3.6`, así que pip en Python 2.7 solo encuentra versiones de Flask hasta la 1.1.4:

```
ERROR: Could not find a version that satisfies the requirement Flask==2.0.3 (from -r requirements.txt (line 1)) (from versions: 0.1, …, 1.1.4)
ERROR: No matching distribution found for Flask==2.0.3 (from -r requirements.txt (line 1))
```

**Corrección.** `FROM python:3.13-slim`:

- **3.13** es la misma versión que usa el job de test (ver 1.2).
- **slim** es una base Debian mínima, sin compiladores ni paquetes extra. No hacen falta, porque todas las dependencias son wheels de Python puro, y así la imagen es más chica y tiene menos superficie de ataque.

### 2.2 Revisar ruta de copia de requirements.txt

**Problema.**

```dockerfile
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt          # el archivo queda en /tmp
RUN pip install --no-cache-dir -r requirements.txt   # pero se busca en /app
```

La ruta relativa de `pip install -r requirements.txt` se resuelve contra el `WORKDIR` (`/app`), donde el archivo no existe:

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

**Corrección.** `COPY requirements.txt .`: el destino `.` es el `WORKDIR` (`/app`). Se mantiene el orden *copiar requirements → instalar → copiar el código*, que aprovecha la caché de capas: las dependencias solo se reinstalan cuando cambia `requirements.txt`.

### 2.3 Corregir error al ejecutar la aplicación

**Problema.** `COPY app/ .` copia el **contenido** de `app/` en `/app` (`main.py` y `test_main.py`). No existe ningún `app.py`:

```
$ docker run brokeapp
python: can't open file '/app/app.py': [Errno 2] No such file or directory
```

El contenedor termina con código 2, así que el job `validate` nunca obtendría respuesta.

**Corrección.** `CMD ["python", "main.py"]`. `main.py` ejecuta `app.run(host='0.0.0.0', port=5000)`: escucha en todas las interfaces, que es lo que necesita `-p 5000:5000`, y en el puerto que declara `EXPOSE 5000`.

---

## 3. APP / Testing — `app/test_main.py`

`app/main.py` (sin modificar) define el comportamiento esperado:

| Ruta | Respuesta | Código |
|---|---|---|
| `GET /health` | `{"status": "OK"}` | 200 |
| `GET /` | `{"message": "Hello! This is a sample CI/CD application"}` | 200 |
| `GET /ping` | (no existe) | 404 |

El test tenía tres defectos, pero pytest mostraba solo dos: el tercero quedaba oculto detrás del 404. Así evolucionó la salida al corregirlos de a uno:

| Paso | Resultado de `pytest app/` |
|---|---|
| Original | ❌ `test_health_endpoint`: `AssertionError: 404 != 200` · ❌ `test_hello_endpoint`: `AssertionError: 200 != 2000` |
| + 3.1 (`2000` → `200`) | ❌ `test_health_endpoint`: `AssertionError: 404 != 200` · ✅ `test_hello_endpoint` |
| + 3.2 (`/ping` → `/health`) | ❌ `test_health_endpoint`: `AssertionError: 'OK' != 'ok'` (recién ahora visible) |
| + 3.3 (`'ok'` → `'OK'`) | ✅ `2 passed` |

### 3.1 Solucionar comportamiento del test

`self.assertEqual(response.status_code, 2000)`: 2000 no es un código de estado HTTP válido (van de 100 a 599). El test no podía pasar nunca, aunque la app respondiera bien. `GET /` responde `200 OK`.

```diff
-        self.assertEqual(response.status_code, 2000)
+        self.assertEqual(response.status_code, 200)
```

### 3.2 Nombre del endpoint de check incorrecto

El test consultaba `/ping`, que no existe en `main.py`, y Flask respondía 404. El health check es `/health`, que es también la ruta que consulta el job `validate`.

```diff
-        response = self.app.get('/ping')
+        response = self.app.get('/health')
```

### 3.3 Valor de respuesta incorrecto

La app responde `{"status": "OK"}`, y `assertEqual` compara strings de forma exacta, distinguiendo mayúsculas de minúsculas.

```diff
-        self.assertEqual(data['status'], 'ok')
+        self.assertEqual(data['status'], 'OK')
```

> **Sobre la asignación de ítems.** Los rótulos 3.1 y 3.3 de la consigna son genéricos. La asignación de arriba es la lectura más directa: el "valor de respuesta" es el valor del campo `status` y el "comportamiento" es la aserción imposible. Con cualquier asignación, los tres defectos del archivo quedan corregidos.

---

## Mejoras adicionales (fuera del checklist)

La consigna pide identificar y corregir *todos* los problemas del repositorio y evalúa las prácticas de seguridad del flujo. Por eso se agregaron estos cuatro cambios. Cada uno está en su propio commit, se puede revertir por separado y se verificó en el run [39514055326](https://github.com/eduair94/BrokeApp/actions/runs/39514055326).

### E1. Nombre del paso de validación

El paso se llamaba `Validate /ping endpoint`, pero consulta `/health`. Pasó a llamarse `Validate /health endpoint`: `main.py` no define `/ping`, y un nombre engañoso confunde al leer los logs de una falla.

### E2. `"$GITHUB_OUTPUT"` entre comillas

```diff
-      run: echo "tag=$(echo '${{ steps.meta.outputs.tags }}' | head -1)" >> $GITHUB_OUTPUT
+      run: echo "tag=$(echo '${{ steps.meta.outputs.tags }}' | head -1)" >> "$GITHUB_OUTPUT"
```

Es la forma que usa la documentación de GitHub y evita el *word splitting* de la variable. En el workflow original, actionlint reportaba `SC2086: Double quote to prevent globbing and word splitting`; con este cambio no reporta ningún hallazgo.

### E3. Contenedor sin privilegios de root

Sin instrucción `USER`, Flask corría como root (uid 0) dentro del contenedor. Ahora:

```dockerfile
FROM python:3.13-slim

RUN useradd --system --no-create-home appuser       # capa temprana: queda en caché

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # todavía como root
COPY app/ .

USER appuser                                         # desde acá, sin privilegios
```

pip instala como root en el `site-packages` del sistema, el código queda de solo lectura para la app y el proceso corre sin privilegios. El puerto 5000 no requiere root. Verificado: `id` dentro del contenedor devuelve `uid=999(appuser)`, intentar escribir en `/app` da `Permission denied` y Docker Scout marca ✓ *Default non-root user*.

### E4. Permisos mínimos del `GITHUB_TOKEN` por job

El bloque `permissions` global (`contents: read`, `packages: write`) le daba a los tres jobs un token capaz de publicar paquetes, aunque solo `build` publica. Se agregaron permisos a nivel job, que **reemplazan por completo** a los globales para ese job. El bloque global no cambió y ahora aplica solo a `build`:

| Job | Qué necesita | Permisos del token (log del runner) |
|---|---|---|
| `test` | checkout | `Contents: read`, `Metadata: read` |
| `build` | checkout + push a GHCR | `Contents: read`, `Metadata: read`, `Packages: write` |
| `validate` | pull desde GHCR | `Metadata: read`, `Packages: read` |

La última columna está copiada de la sección *GITHUB_TOKEN Permissions* del log de cada job del run 39514055326, donde el pull con `packages: read` funcionó.

---

## Prácticas de seguridad del flujo

Criterio 5 de la evaluación:

- **Permisos mínimos y explícitos** del `GITHUB_TOKEN`, global y por job (E4). El permiso por defecto del repo es de solo lectura.
- **Sin credenciales guardadas:** el login a GHCR usa el `GITHUB_TOKEN` efímero de cada run (`secrets.GITHUB_TOKEN`).
- **Los pull requests no publican:** `push: ${{ github.event_name != 'pull_request' }}`, y `validate` no corre en PRs. Un PR, por ejemplo desde un fork, nunca sube una imagen al registry.
- **Contexto de build acotado:** `.dockerignore` excluye `.git`, `.github` y cachés.
- **Imagen base mantenida y mínima** (`python:3.13-slim`) y **proceso sin root** (E3).
- **Trazabilidad:** cada imagen se etiqueta con el SHA corto del commit, además de `main`, y `docker/build-push-action` agrega una attestation de *provenance* (`--attest type=provenance,mode=max` en el log del build).

Se conservaron todas las prácticas que ya traía el workflow. Ningún problema se resolvió ampliando permisos.

---

## Verificación

### Local

- **Simulación del workflow** (ver [Metodología](#metodología)): workflow original → 4 fallas (trigger, setup de Python 3.1, build de Docker, validate); con los 10 fixes del checklist → 12/12 chequeos OK; con las mejoras → 12/12 OK.
- **actionlint 1.7.12:** workflow original → 1 hallazgo (SC2086); final → 0.
- **Contenedor:** `GET /health` → `{"status":"OK"}` (200), `GET /` → `{"message":"Hello! This is a sample CI/CD application"}` (200), `GET /ping` → 404.

### GitHub Actions (fork)

Extracto de los logs del run [39513506166](https://github.com/eduair94/BrokeApp/actions/runs/39513506166), el de solo checklist (job, seguido de la línea del log):

```
Test      Image: ubuntu-24.04
Test      Successfully set up CPython (3.13.16)
Test      ======================== 2 passed, 89 warnings in 0.22s ========================
Build     #11 pushing manifest for ghcr.io/eduair94/brokeapp:main@sha256:affc3a98d1edcbbbd38dc79d0a7e25f35ebd1bbfdb7908407e9dc85af0416692
Build     #11 pushing manifest for ghcr.io/eduair94/brokeapp:9c6591e@sha256:affc3a98d1edcbbbd38dc79d0a7e25f35ebd1bbfdb7908407e9dc85af0416692
Validate  Status: Downloaded newer image for ghcr.io/eduair94/brokeapp:main
Validate  Response: {"status":"OK"}
Validate  Response: {"message":"Hello! This is a sample CI/CD application"}
```

Dos detalles del pipeline confirmados en los logs:

- `docker/metadata-action` pasa el nombre de la imagen a minúsculas (`eduair94/BrokeApp` → `ghcr.io/eduair94/brokeapp`), como exige Docker. Por eso el workflow funciona aunque el nombre del repo tenga mayúsculas.
- El job `validate` usa la primera etiqueta de la lista (`head -1`). metadata-action las ordena por prioridad (`type=ref,event=branch` = 600, `type=sha` = 100), así que valida `:main`, que en ese momento apunta a la imagen recién publicada.

La imagen es pública: `docker pull ghcr.io/eduair94/brokeapp:main`.

---

## Observaciones y recomendaciones (no aplicadas)

Estos puntos quedan fuera de la consigna o requieren cambiar archivos o versiones que la consigna fija:

1. **Dependencias con vulnerabilidades conocidas.** Docker Scout sobre la imagen final:

   | Paquete (fijado en `requirements.txt`) | Severidad | CVE | Corregido en |
   |---|---|---|---|
   | Werkzeug 2.0.3 | Crítica | CVE-2022-29361 | 2.1.1 |
   | Werkzeug 2.0.3 | Alta | CVE-2023-25577 | 2.2.3 |
   | Werkzeug 2.0.3 | Alta | CVE-2024-34069 | 3.0.3 |
   | Flask 2.0.3 | Alta | CVE-2023-30861 | 2.2.5 |

   Corregirlas exige Werkzeug ≥ 3.0.3, que **no es compatible con Flask 2.0.3** (verificado: `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'`), así que también hay que actualizar Flask. Se probó `Flask==3.1.3`, `Werkzeug==3.1.9` y `pytest==9.1.1` en Python 3.14: con el mismo `main.py` y los mismos tests da `2 passed` **sin warnings**, y las respuestas JSON tienen el formato que espera `validate`. No se aplicó porque cambia el stack que fija la consigna.

2. **Vulnerabilidades de la imagen base.** Las 6 vulnerabilidades altas que reportan los escáneres para `python:3.13-slim` (por ejemplo, la extensión de Docker del IDE) vienen de librerías que **pip trae vendorizadas** (urllib3 2.7.0, msgpack 1.1.2 y `pkg_resources` de setuptools 70.3.0, declaradas en `pip/_vendor/bom.cdx.json`) y de zlib de Debian 13, que no tiene fix publicado. Se mitigan reconstruyendo la imagen periódicamente sobre la última `python:3.13-slim` (por ejemplo, con Dependabot) o con un build multi-stage que no deje pip en la imagen final.

3. **Servidor de desarrollo en producción.** `main.py` usa `app.run()`, y el propio log lo advierte: `WARNING: This is a development server. Do not use it in a production deployment.` Lo correcto sería un servidor WSGI como gunicorn, pero eso cambia cómo arranca la app, y `main.py` no se puede modificar.

4. **Herramientas de test en la imagen de producción.** `pytest` (porque está en `requirements.txt`) y `test_main.py` (por `COPY app/ .`) terminan en la imagen. Se puede separar un `requirements-dev.txt` y excluir los tests con `.dockerignore`.

5. **La espera de `validate` no falla por sí misma.** Si la app nunca responde, el bucle de `Wait for app to be ready` termina con el código del último comando (`sleep 2`, que devuelve 0) y el paso queda en verde; el error lo detecta recién el paso siguiente. Convendría un `exit 1` explícito después del último intento.

6. **Fijar las actions por SHA**, en lugar de `@v6`, `@v7`, etc., y habilitar Dependabot para `github-actions` y `docker`.

7. **Builds reproducibles.** Solo están fijadas las dependencias directas; las transitivas (Jinja2, click, itsdangerous, MarkupSafe…) se resuelven en cada build. Un lockfile (pip-tools, uv) lo resolvería.

---

## Cómo reproducir localmente

Requiere Docker. Desde la raíz del repo:

```bash
# Tests, con el mismo runtime que usa CI
docker run --rm -v "$PWD":/w -w /w -e PYTHONDONTWRITEBYTECODE=1 python:3.13-slim \
  sh -c "pip install -q -r requirements.txt && python -m pytest -p no:cacheprovider app/"

# Imagen + lo mismo que hace el job validate
docker build -t brokeapp .
docker run -d -p 5000:5000 --name app brokeapp
curl -s http://localhost:5000/health   # {"status":"OK"}
curl -s http://localhost:5000/         # {"message":"Hello! This is a sample CI/CD application"}
docker rm -f app
```

---

## Historial de commits

Un commit por problema, en el orden del checklist. Cada mensaje explica la causa y la corrección:

```
0f02057 fix(ci): disparar el pipeline con push a main
48c44fa fix(ci): usar Python 3.13 en el job de test
a9e4c67 fix(ci): corregir el nombre del archivo de dependencias
9eddae1 fix(ci): ejecutar pytest sobre app/, donde están los tests
0412c76 fix(docker): actualizar la imagen base a python:3.13-slim
9770c21 fix(docker): copiar requirements.txt al WORKDIR
6290d7d fix(docker): ejecutar main.py en lugar de app.py
5ba7cab fix(test): esperar HTTP 200 en / (no 2000)
ea0e467 fix(test): consultar /health, el endpoint que define la app
9c6591e fix(test): esperar status "OK", tal como responde la app
105d06a fix(ci): nombrar el paso de validación según el endpoint real
ea32d87 ci: citar $GITHUB_OUTPUT en el paso "Save image tag"
ec7642a build(docker): ejecutar la aplicación con un usuario sin privilegios
d83b680 ci: permisos mínimos por job (least privilege)
```

Después vienen los commits de documentación: este archivo y el checklist del README marcado como resuelto.
