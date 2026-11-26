# Práctica Semana 13 — APIs REST con Django REST Framework

Proyecto con los dos casos del enunciado: API REST para la biblioteca universitaria y API de comercio electrónico TecnoMarket Perú. El informe PDF es responsabilidad del estudiante y no está incluido.

## Ejecutar en VS Code (Windows)
Abre esta carpeta (contiene `manage.py`) y ejecuta en PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Vista principal: http://127.0.0.1:8000/

Catálogos HTML: `/catalogo/libros/` y `/catalogo/productos/`. Los endpoints JSON siguen disponibles bajo `/api/biblioteca/libros/` y `/api/productos/`.

Swagger: http://127.0.0.1:8000/api/docs/ — ReDoc: http://127.0.0.1:8000/api/redoc/ — Admin: http://127.0.0.1:8000/admin/

## Caso 1: Biblioteca
API raíz `http://127.0.0.1:8000/api/biblioteca/`: `autores/`, `libros/`, `prestamos/`, `prestamos/vencidos/`, `prestamos/{id}/devolver/`. Filtros de libros: `categoria`, `anio`, `disponible=true`; búsqueda `search=`; orden `ordering=anio` o `ordering=titulo`. Paginación de 20.

Usuarios muestra: `admin/admin12345`, `bibliotecario/biblio12345`, `estudiante01` a `estudiante10` con `estudiante123`. Token: POST `/api/token/` con username/password.

## Caso 2: TecnoMarket
API raíz `http://127.0.0.1:8000/api/`: `productos/`, `categorias/`, `carrito/`, `ordenes/`, `resenas/`. Carrito: POST `carrito/agregar/`, `actualizar/`, `eliminar/`, `vaciar/`, `checkout/`. Productos filtra por categoría, marca, rango de precio y disponibilidad; `search=` y `ordering=`. Descuento de demostración: cupón `TECNO10`.

Usuarios muestra: `admin/admin12345`, `cliente01` a `cliente20` con `cliente123`, y `vendedor01` a `vendedor05` con `vendedor123`. Ejecutar `seed_market` carga 100 productos de muestra.

## Comandos
`python manage.py test` — `python manage.py check` — `python manage.py spectacular --file schema.yml`.

Las rutas de biblioteca se distinguen con el prefijo `/api/biblioteca/`; TecnoMarket usa `/api/`. Tokens se obtienen con POST `/api/token/` y `{ "username": "cliente01", "password": "cliente123" }`, luego se envía `Authorization: Token <token>`.

