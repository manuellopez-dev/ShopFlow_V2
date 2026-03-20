<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1e3a8a,100:2563eb&height=140&section=header&text=ShopFlow&fontSize=48&fontColor=ffffff&fontAlignY=65&animation=fadeIn" width="100%"/>

### Plataforma E-Commerce Full Stack con RBAC, 2FA y Pagos Reales

*Python · Flask · MySQL · JWT · Stripe · PayPal*

<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-635BFF?style=for-the-badge&logo=stripe&logoColor=white)
![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-2563eb?style=for-the-badge)](https://shopflow-v2.onrender.com)
[![Repo](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/manuellopez-dev/ShopFlow_V2)

</div>

---

## 📌 ¿Qué es ShopFlow?

ShopFlow es una plataforma de comercio electrónico Full Stack desarrollada con Python y Flask, orientada a pequeñas y medianas empresas que necesitan un sistema seguro, con roles diferenciados y pagos reales integrados.

El proyecto implementa patrones de seguridad de nivel profesional: autenticación con JWT y refresh tokens, doble factor de autenticación (2FA) con Google Authenticator, control de acceso basado en roles (RBAC) y protección contra fuerza bruta con rate limiting.

---

## ✨ Funcionalidades por módulo

### 🔐 Autenticación y Seguridad
- Registro y login con JWT de corta duración + refresh token
- **2FA obligatorio para Administrador** — TOTP con `pyotp`, compatible con Google Authenticator
- Recuperación de contraseña con token de un solo uso (TTL: 15 minutos) vía email
- Contraseñas hasheadas con `bcrypt`
- Rate limiting en endpoints de auth con `Flask-Limiter`
- Variables de entorno con `python-dotenv`, nunca versionadas en el repositorio
- Indicador de fortaleza de contraseña en el registro

### 👥 Control de Acceso por Roles (RBAC)

| Rol | Acceso |
|---|---|
| **Administrador** | Gestión total: usuarios, categorías, pedidos, cupones, dashboard con estadísticas y gráficas |
| **Vendedor** | Crear y editar productos, descuentos por cantidad, historial de precios, dashboard de ventas |
| **Cliente** | Catálogo con filtros, carrito, cupones, pagos, favoritos, reseñas, historial de pedidos y perfil |

### 🛍️ Catálogo y Tienda
- Catálogo de productos con búsqueda en tiempo real, filtros por categoría, precio y ordenamiento
- Imágenes de productos (URL o subida desde PC)
- Sistema de favoritos por cliente
- Reseñas con calificación de estrellas (1-5) e indicador interactivo
- Descuentos por cantidad configurables por el vendedor
- Alertas automáticas de stock bajo por email
- Productos relacionados en la vista de detalle

### 🛒 Carrito y Pedidos
- Carrito persistente por sesión
- Aplicación de cupones con validación de vigencia, tipo (porcentaje/monto fijo) y límite de usos
- Flujo de compra: Carrito → Checkout → **Dirección de envío** → Pago
- Gestión de estados de pedido: Pendiente → Confirmado → Enviado → Entregado → Cancelado
- Historial de pedidos con detalle completo y dirección de envío
- Paginación en todas las tablas

### 💳 Pagos
- **Stripe** — campos separados para número, fecha y CVC con validación en tiempo real
- **PayPal** — redirección al sandbox de PayPal
- Confirmación automática del pago y cambio de estado del pedido
- Notificación por email al cliente y al vendedor al completar una compra

### 📧 Notificaciones por Email
- Recuperación de contraseña con enlace seguro
- Actualización de estado de pedido al cliente
- Nueva venta al vendedor con detalle de productos
- Alerta de stock bajo al vendedor
- Templates HTML diseñados con gradientes y estilos profesionales

### 📊 Dashboards
- **Admin:** estadísticas globales, ingresos últimos 7 días, pedidos por estado (dona), productos más vendidos (barras), pedidos recientes
- **Vendor:** productos activos, unidades vendidas, ingresos totales, alerta de stock bajo, ventas últimos 7 días, productos más vendidos, ventas recientes

### 🌙 UI/UX
- Modo oscuro / modo claro con toggle persistente en `localStorage`
- Diseño responsive completo con navbar hamburguesa en móvil
- Toast notifications (ventanas flotantes) para mensajes del sistema
- Modales de confirmación antes de acciones destructivas
- Animaciones en catálogo: fade in, zoom en hover, stagger por card
- Páginas de error 404 y 500 personalizadas
- Indicador de progreso en el flujo de compra (Pedido → Envío → Pago)

### 📚 Documentación
- Manual de usuario con guías por rol y preguntas frecuentes
- Documentación de API con endpoints, métodos, parámetros y roles requeridos
- Diagrama de base de datos con tablas, relaciones PK/FK y tipos de datos

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Propósito |
|---|---|---|
| Frontend | HTML5 + CSS3 + JS + Jinja2 | Vistas renderizadas en servidor |
| Iconos | Lucide Icons | Iconografía moderna y consistente |
| Gráficas | Chart.js | Dashboards interactivos |
| Backend | Python 3 + Flask | Rutas, lógica de negocio y seguridad |
| Base de datos | MySQL + SQLAlchemy | ORM y almacenamiento relacional |
| Autenticación | Flask-JWT-Extended + Flask-Bcrypt | Tokens JWT y hashing de contraseñas |
| 2FA | pyotp + qrcode | TOTP compatible con Google Authenticator |
| Pagos | Stripe + PayPal SDK | Procesamiento de pagos reales |
| Email | Flask-Mail + Gmail SMTP | Notificaciones automáticas |
| Seguridad | Flask-Limiter + Flask-WTF | Rate limiting y protección CSRF |
| Despliegue | Render.com + filess.io | Hosting cloud con BD MySQL externa |

---

## 🏗️ Arquitectura del proyecto
```
ShopFlow_V2/
├── app/
│   ├── __init__.py           # Factory pattern, inicialización de Flask
│   ├── extensions.py         # Extensiones Flask (db, jwt, mail, etc.)
│   ├── models/
│   │   ├── user.py           # Usuario, roles, RBAC
│   │   ├── product.py        # Producto, reseñas, favoritos, descuentos
│   │   ├── order.py          # Pedido, items, cupones
│   │   └── category.py       # Categorías
│   ├── routes/
│   │   ├── auth.py           # Login, registro, 2FA, reset password
│   │   ├── admin.py          # Dashboard admin, usuarios, pedidos, categorías
│   │   ├── vendor.py         # Dashboard vendor, productos, descuentos
│   │   ├── client.py         # Catálogo, carrito, checkout, envío, pedidos
│   │   ├── coupons.py        # Gestión y aplicación de cupones
│   │   ├── reviews.py        # Reseñas y favoritos
│   │   └── payments.py       # Stripe y PayPal
│   ├── utils/
│   │   ├── email.py          # Templates y envío de emails
│   │   ├── security.py       # JWT callbacks
│   │   ├── sanitize.py       # Sanitización de inputs
│   │   └── decorators.py     # Decoradores de roles
│   ├── templates/
│   │   ├── base.html         # Layout principal con navbar dinámico
│   │   ├── auth/             # Login, register, 2FA, reset password
│   │   ├── admin/            # Dashboard, usuarios, pedidos, categorías, cupones
│   │   ├── vendor/           # Dashboard, productos, descuentos, precios
│   │   ├── client/           # Catálogo, carrito, checkout, envío, pago, perfil
│   │   ├── main/             # Index, manual, API docs, diagrama BD
│   │   ├── errors/           # 404, 500
│   │   └── macros/           # Paginación reutilizable
│   └── static/
│       ├── css/style.css     # Design system completo con modo oscuro
│       └── js/
│           ├── animations.js      # Scroll reveal, contadores, ripple
│           ├── ui.js              # Toasts, modales de confirmación
│           ├── darkmode.js        # Toggle modo oscuro persistente
│           ├── dashboard.js       # Gráficas admin (Chart.js)
│           ├── vendor_dashboard.js # Gráficas vendor (Chart.js)
│           ├── particles-config.js # Partículas en hero
│           ├── checkout.js        # Aplicación de cupones
│           ├── payment.js         # Integración Stripe Elements
│           └── product_detail.js  # Selector de cantidad y star rating
├── config.py                 # Configuración por entorno (dev/prod)
├── run.py                    # Punto de entrada
├── requirements.txt
├── Procfile                  # Para despliegue en Render
└── .env.example              # Variables de entorno de referencia
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
python -c "
from dotenv import load_dotenv; load_dotenv()
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Tablas creadas OK')
"

# 6. Ejecutar
python run.py
```

---

## 🔑 Variables de entorno requeridas
```env
# Flask
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta

# Base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=shopflow

# JWT
JWT_SECRET_KEY=tu_jwt_secret

# Email (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_app_password
MAIL_DEFAULT_SENDER=tu_correo@gmail.com

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...

# PayPal
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_MODE=sandbox
```

---

## 🔒 Seguridad — decisiones técnicas destacadas

**JWT + sesión Flask como fallback** — los tokens JWT se almacenan en cookies HTTP-only. Se usa la sesión Flask como fallback para navegadores que no envían cookies en redirects.

**Respuestas genéricas en auth** — los endpoints de login devuelven el mismo mensaje de error independientemente del motivo, evitando user enumeration.

**2FA solo para Admin** — el rol con más privilegios requiere TOTP en cada inicio de sesión, compatible con Google Authenticator y Authy.

**Rate limiting por IP** — los endpoints de autenticación tienen límite de intentos con `Flask-Limiter`, mitigando ataques de fuerza bruta.

**Sanitización de inputs** — todos los inputs del usuario se sanitizan con `bleach` antes de guardarse.

**Variables de entorno** — ninguna credencial está hardcodeada. El `.env` está en `.gitignore`.

---

## 🧪 Usuarios de prueba

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | admin@shopflow.com | Admin123! |
| Vendedor | vendor@shopflow.com | Vendor123! |
| Cliente | luismanuel141205@gmail.com | Client123! |

**Stripe test card:** `4242 4242 4242 4242` · Fecha: `12/26` · CVC: `123`

> El Admin requiere 2FA. Configúralo desde el panel de administración con Google Authenticator.

---

## 🌐 Demo en vivo

[https://shopflow-v2.onrender.com](https://shopflow-v2.onrender.com)

> ⚠️ La instancia gratuita de Render puede tardar hasta 50 segundos en despertar si estuvo inactiva.

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir con atribución.

---

<div align="center">

Desarrollado por **Luis Manuel López Cano**

Materia: Desarrollo de Aplicaciones Web · Cuatrimestre 8 · 2026

[GitHub](https://github.com/manuellopez-dev) · [LinkedIn](https://www.linkedin.com/in/luis-manuel-lopez-cano-692984390/) · [manuel.lopez.engineer@gmail.com](mailto:manuel.lopez.engineer@gmail.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2563eb,50:1e3a8a,100:0f172a&height=80&section=footer" width="100%"/>

</div>
