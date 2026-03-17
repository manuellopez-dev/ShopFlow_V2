<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1a2e,100:6DB33F&height=140&section=header&text=ShopFlow&fontSize=48&fontColor=ffffff&fontAlignY=65&animation=fadeIn" width="100%"/>

### Plataforma E-Commerce Full Stack con RBAC, 2FA y Pagos Reales

*Python · Flask · MySQL · JWT · Stripe · PayPal*

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)
![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-6DB33F?style=for-the-badge)](https://shopflow.pythonanywhere.com)
[![Repo](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/manuellopez-dev/ShopFlow_V2)

</div>

---

## 📌 ¿Qué es ShopFlow?

ShopFlow es una plataforma de comercio electrónico Full Stack desarrollada con Python y Flask, orientada a pequeñas y medianas empresas que necesitan un sistema seguro, con roles diferenciados y pagos reales integrados.

El proyecto implementa patrones de seguridad de nivel profesional: autenticación con JWT y refresh tokens rotativos, doble factor de autenticación (2FA) con Google Authenticator, control de acceso basado en roles (RBAC) y protección contra fuerza bruta con rate limiting.

---

## ✨ Funcionalidades por módulo

### 🔐 Autenticación y Seguridad
- Registro y login con JWT de corta duración + refresh token rotativo
- **2FA obligatorio para Administrador** — TOTP con `pyotp`, compatible con Google Authenticator
- Recuperación de contraseña con token de un solo uso (TTL: 15 minutos) vía email
- Contraseñas hasheadas con `bcrypt` (salt rounds ≥ 12)
- Rate limiting en endpoints de auth con `Flask-Limiter` para mitigar fuerza bruta
- Cabeceras de seguridad HTTP con `Flask-Talisman` + HTTPS forzado en producción
- Variables de entorno con `python-dotenv`, nunca versionadas en el repositorio

### 👥 Control de Acceso por Roles (RBAC)

| Rol | Acceso |
|---|---|
| **Administrador** | Gestión total: usuarios, productos, pedidos, cupones, reportes y configuración |
| **Vendedor** | Alta y edición de sus productos, visualización de pedidos asignados |
| **Cliente** | Catálogo, carrito, pagos, favoritos, historial de pedidos y reseñas |

Cada rol está protegido con decoradores personalizados en Flask que verifican permisos en cada ruta.

### 🛍️ Catálogo y Tienda
- Catálogo de productos con categorías, imágenes, precio y stock
- Sistema de favoritos por cliente
- Comentarios y calificaciones en productos
- Reglas de stock automáticas — alerta cuando el inventario está bajo
- Búsqueda y filtros por categoría, precio y disponibilidad

### 🛒 Carrito y Pedidos
- Carrito persistente por sesión de usuario
- Aplicación de cupones de descuento con validación de vigencia y límite de usos
- Gestión completa de pedidos con estados rastreables
- Historial de compras por cliente

### 💳 Pagos
- **Stripe** — pagos con tarjeta de crédito/débito
- **PayPal** — checkout con cuenta PayPal
- Webhooks para confirmación automática de pagos
- Manejo de errores y pagos fallidos

### 📊 Dashboard y Reportes (Admin)
- Gráficas de ventas por período (diario, semanal, mensual)
- Producto más vendido, vendedor más activo
- Exportación de reportes

### 🌙 UI/UX
- Modo oscuro / modo claro con toggle persistente
- Diseño responsive con HTML5 + CSS3 + JavaScript vanilla
- Plantillas renderizadas en servidor con Jinja2

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| Frontend | HTML5 + CSS3 + JS + Jinja2 | Vistas renderizadas en servidor |
| Backend | Python 3 + Flask | Rutas, lógica de negocio y seguridad |
| Base de datos | MySQL + SQLAlchemy | ORM y almacenamiento relacional |
| Autenticación | Flask-JWT-Extended + Flask-Bcrypt | Tokens JWT y hashing de contraseñas |
| 2FA | pyotp + qrcode | TOTP compatible con Google Authenticator |
| Pagos | Stripe + PayPal SDK | Procesamiento de pagos reales |
| Email | Flask-Mail + Gmail SMTP | Recuperación de contraseña y notificaciones |
| Seguridad | Flask-Talisman + Flask-Limiter | Cabeceras HTTP y rate limiting |
| Despliegue | PythonAnywhere / Render | Hosting cloud con soporte nativo Flask |

---

## 🏗️ Arquitectura del proyecto

```
ShopFlow_V2/
├── app/
│   ├── __init__.py          # Factory pattern, inicialización de Flask
│   ├── models/              # Modelos SQLAlchemy (User, Product, Order, Coupon...)
│   ├── routes/              # Blueprints por módulo (auth, shop, admin, vendedor)
│   ├── services/            # Lógica de negocio desacoplada de las rutas
│   ├── decorators/          # Decoradores de roles y autenticación
│   ├── templates/           # Plantillas Jinja2
│   └── static/              # CSS, JS, imágenes
├── config.py                # Configuración por entorno (dev/prod)
├── run.py                   # Punto de entrada
├── requirements.txt
├── Procfile                 # Para despliegue en Render
└── .env.example             # Variables de entorno de referencia
```

---

## ⚙️ Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/manuellopez-dev/ShopFlow_V2.git
cd ShopFlow_V2

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales

# 5. Inicializar la base de datos
flask db upgrade

# 6. Ejecutar
flask run
```

---

## 🔑 Variables de entorno requeridas

```env
# Base de datos
DATABASE_URL=mysql+pymysql://user:password@localhost/shopflow

# JWT
JWT_SECRET_KEY=tu_clave_secreta

# Email (Gmail SMTP)
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Entorno
FLASK_ENV=development
```

---

## 🔒 Seguridad — decisiones técnicas destacadas

**Refresh tokens rotativos** — cada vez que el cliente usa un refresh token para obtener un nuevo access token, el anterior queda invalidado. Esto previene el reuso de tokens robados.

**Respuestas genéricas en auth** — los endpoints de login y registro devuelven el mismo mensaje de error independientemente de si el email no existe o la contraseña es incorrecta, evitando user enumeration.

**2FA solo para Admin** — el rol con más privilegios requiere TOTP en cada inicio de sesión. Se genera un QR al registrar el admin, compatible con Google Authenticator y Authy.

**Rate limiting por IP** — los endpoints `/login`, `/register` y `/recuperar-password` tienen límite de intentos por IP con `Flask-Limiter`, mitigando ataques de fuerza bruta.

**Variables de entorno** — ninguna credencial está hardcodeada. El `.env` está en `.gitignore` y el repositorio incluye `.env.example` como referencia.

---

## 🧪 Usuarios de prueba

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | admin@shopflow.com | Admin123! |
| Vendedor | vendedor@shopflow.com | Vendedor123! |
| Cliente | cliente@shopflow.com | Cliente123! |

> El Admin requiere 2FA. Usa Google Authenticator con el QR disponible en el panel de configuración.

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir con atribución.

---

<div align="center">

Desarrollado por **Luis Manuel López Cano**
[GitHub](https://github.com/manuellopez-dev) · [LinkedIn](https://www.linkedin.com/in/luis-manuel-lopez-cano-692984390/) · [manuel.lopez.engineer@gmail.com](mailto:manuel.lopez.engineer@gmail.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6DB33F,50:1a1a2e,100:0d1117&height=80&section=footer" width="100%"/>

</div>
