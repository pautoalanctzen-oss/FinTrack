# 🚀 Guía de Despliegue - FinTrack

## 📋 Requisitos previos
- Cuenta de GitHub (gratis)
- Cuenta de Vercel (gratis)
- Cuenta de Render (gratis)

---

## 🎯 Paso 1: Subir código a GitHub

### Opción A: Si NO tienes repositorio
1. Ve a [github.com](https://github.com) e inicia sesión
2. Clic en "New repository"
3. Nombre: `aplicacion-mi` (o el que prefieras)
4. Marca como **Público**
5. NO agregues README, .gitignore ni license (ya los tenemos)
6. Clic en "Create repository"

### Ejecuta en PowerShell:
```powershell
# Navega a tu proyecto
cd "c:\Users\pauto\OneDrive\Escritorio\Uni Docs\9 semestre\Integradora\Solución MI"

# Inicializar Git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Versión final lista para despliegue"

# Conectar con GitHub (REEMPLAZA con tu URL)
git remote add origin https://github.com/TU-USUARIO/aplicacion-mi.git

# Subir código
git branch -M main
git push -u origin main
```

---

## 🌐 Paso 2: Desplegar Backend en Render

1. Ve a [render.com](https://render.com)
2. Clic en "Get Started" → Sign up con GitHub
3. Clic en "New +" → "Web Service"
4. Conecta tu repositorio `aplicacion-mi`
5. Configuración:
   - **Name**: `mi-backend-api`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

6. Clic en "Create Web Service"
7. Espera ~5 minutos mientras despliega
8. **¡IMPORTANTE!** Guarda tu URL: `https://mi-backend-api.onrender.com`

---

## 🎨 Paso 3: Desplegar Frontend en Vercel

1. Ve a [vercel.com](https://vercel.com)
2. Clic en "Start Deploying" → Sign up con GitHub
3. Clic en "Import Project"
4. Busca y selecciona tu repo `aplicacion-mi`
5. Configuración:
   - **Project Name**: `aplicacion-mi`
   - **Framework Preset**: `Other`
   - **Root Directory**: `frontend`
   - **Build Command**: (dejar vacío)
   - **Output Directory**: (dejar vacío)

6. Clic en "Deploy"
7. Espera ~2 minutos
8. **¡IMPORTANTE!** Guarda tu URL: `https://aplicacion-mi.vercel.app`

---

## 🔗 Paso 4: Conectar Frontend con Backend

Necesitas actualizar la URL del backend en tu frontend:

1. Abre `frontend/dashboard.html`
2. Busca la línea con `const BASE_API`
3. Reemplaza con tu URL de Render:
```javascript
const BASE_API = 'https://mi-backend-api.onrender.com';
```

4. Guarda y sube cambios:
```powershell
git add frontend/dashboard.html
git commit -m "Actualizar URL del backend"
git push
```

5. Vercel detectará el cambio y se actualizará automáticamente en ~1 minuto

---

## ✅ ¡Listo! Tu aplicación está en línea

🌐 **URL de tu aplicación**: `https://aplicacion-mi.vercel.app`

### Comparte este link con quien quieras:
- Se puede abrir desde cualquier navegador
- Funciona en móviles y computadoras
- Disponible 24/7

---

## 🔄 Para hacer cambios después

1. Edita los archivos localmente
2. Guarda cambios:
```powershell
git add .
git commit -m "Descripción de cambios"
git push
```
3. Automáticamente se actualizan:
   - Vercel (frontend): ~1 minuto
   - Render (backend): ~5 minutos

---

## 📊 Monitoreo

- **Vercel Dashboard**: Ver logs y tráfico del frontend
- **Render Dashboard**: Ver logs y estado del backend

---

## ⚠️ Notas importantes

- **Base de datos**: SQLite no es ideal para producción. Para versión final considera PostgreSQL en Render (también gratis)
- **Primer acceso**: El backend puede tardar ~30 segundos en "despertar" si no se usa por un rato (limitación del plan gratuito)
- **Límites gratuitos**: 
  - Vercel: 100 GB bandwidth/mes
  - Render: 750 horas/mes (suficiente para 1 servicio 24/7)

---

## 🆘 Soporte

Si algo no funciona:
1. Revisa los logs en Render/Vercel
2. Verifica que las URLs estén correctas
3. Confirma que el backend esté en estado "Live" en Render
