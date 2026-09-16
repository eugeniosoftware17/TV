# Cloud Screen

Sistema web para gestionar presentaciones y proyectarlas en televisores con conexión a Internet y navegador web.

Permite crear y modificar presentaciones desde una computadora. Cada TV muestra la presentación mediante un enlace web único, sin necesidad de llevar videos físicamente a cada televisor.

## Tecnologías

- Python 3
- Django 5
- HTML5, CSS3, JavaScript
- SQLite
- Django Templates

## Estructura del proyecto

```text
├── manage.py
├── config/              # Configuración Django
├── app/
│   ├── accounts/        # Autenticación
│   ├── presentations/   # Presentaciones y diapositivas
│   ├── screens/         # Pantallas / TV
│   └── core/            # Dashboard, logs, utilidades
├── templates/
├── static/
├── media/
└── requirements.txt
```

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor

```bash
python manage.py runserver
```

Accede a: http://127.0.0.1:8000/

## Uso

### Crear una presentación

1. Inicia sesión con tu usuario administrador.
2. Ve a **Presentaciones** → **+ Nueva presentación**.
3. Completa nombre, descripción y estado.
4. En el **Editor**, crea diapositivas (texto, imagen, video o mixta).
5. Arrastra las diapositivas para reordenarlas.

### Abrir en una TV

1. En el detalle o editor de la presentación, copia el **enlace público**.
2. Abre ese enlace en el navegador del televisor.

Ejemplo:

```text
http://127.0.0.1:8000/p/TOKEN_UNICO/
```

La TV mostrará la presentación en pantalla completa, reproduciendo diapositivas automáticamente.

### Registrar pantallas (opcional en Fase 1)

Ve a **Pantallas** para registrar televisores. En la Fase 2 se habilitará vinculación individual, QR y estado online en tiempo real.

## WebSockets (Fase 2)

La actualización en tiempo real con Django Channels se implementará en la Fase 2. El archivo `config/asgi.py` ya está preparado para esta integración.

Pasos previstos:

1. Instalar `channels`, `channels-redis` y `daphne`.
2. Configurar `CHANNEL_LAYERS` en settings.
3. Crear consumer WebSocket por token de presentación.
4. Emitir señal al guardar presentación/diapositiva.

## Formatos multimedia soportados

| Tipo      | Extensiones                          |
| --------- | ------------------------------------ |
| Imagen    | JPG, JPEG, PNG, WEBP, GIF            |
| Video     | MP4, WEBM                            |
| Documento | PDF (visualización básica en Fase 2) |

PowerPoint (.pptx) requerirá conversión server-side en una fase posterior.

## Seguridad

- Rutas administrativas protegidas con `@login_required`
- CSRF en todos los formularios
- Tokens de presentación generados con `secrets.token_urlsafe`
- Validación de archivos subidos
- Enlace público solo expone la presentación asociada al token

## Licencia

Proyecto privado — Cloud Screen.
