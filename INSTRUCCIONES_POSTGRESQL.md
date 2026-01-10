# 🚀 Solución Definitiva: Base de Datos Permanente con PostgreSQL

## ⚠️ PROBLEMA ACTUAL
- **Render borra SQLite** cada vez que el servidor se reinicia
- **Los datos se pierden** al cerrar o actualizar la aplicación
- Necesitas una base de datos que **persista para siempre**

## ✅ SOLUCIÓN: PostgreSQL Gratuito de Render
**PostgreSQL es una base de datos permanente** que NUNCA pierde datos.

---

## 📋 PASOS PARA CONFIGURAR (5 minutos)

### Paso 1: Subir cambios a GitHub
```powershell
cd "c:\Users\pauto\OneDrive\Escritorio\Uni Docs\9 semestre\Integradora\Solución MI"

git add .
git commit -m "Migración a PostgreSQL para persistencia permanente"
git push
```

### Paso 2: Crear Base de Datos PostgreSQL en Render

1. Ve a [render.com](https://dashboard.render.com/)
2. Clic en "**New +**" → "**PostgreSQL**"
3. Configuración:
   - **Name**: `aplicacion-mi-db`
   - **Database**: `aplicacion_mi_db`
   - **User**: `aplicacion_user`
   - **Region**: Oregon (US West)
   - **PostgreSQL Version**: 16
   - **Plan**: **Free**
   
4. Clic en "**Create Database**"
5. **¡IMPORTANTE!** Espera 2-3 minutos mientras se crea
6. Copia la **Internal Database URL** (la que dice `postgres://...`)

### Paso 3: Configurar Backend con la Base de Datos

1. En Render, ve a tu servicio **aplicacion-mi-backend**
2. Ve a "**Environment**" (en el menú lateral)
3. Clic en "**Add Environment Variable**"
4. Agregar:
   - **Key**: `DATABASE_URL`
   - **Value**: Pega la Internal Database URL que copiaste
   
5. Clic en "**Save Changes**"
6. El servidor se **reiniciará automáticamente** (tarda ~2 minutos)

### Paso 4: Verificar que Funciona

1. Abre el link de tu aplicación: `https://aplicacion-mi.vercel.app`
2. Intenta hacer login con cualquier usuario
3. Si no existe, créalo desde "Registrarse"
4. **¡Los datos ahora persisten para siempre!**

---

## 🔧 RECUPERAR DATOS ANTERIORES

Si ya habías migrado datos antes, necesitas hacerlo de nuevo una vez:

### Opción 1: Usar el endpoint de importación

1. Asegúrate de tener tu backup en `backups/api_snapshot_2026-01-09.json`
2. Abre la consola de desarrollador (F12) en el navegador
3. Pega y ejecuta:

```javascript
const formData = new FormData();
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.onchange = async (e) => {
    formData.append('file', e.target.files[0]);
    const response = await fetch('https://aplicaci-n-mi.onrender.com/api/import-backup', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    console.log('Importación:', result);
};
fileInput.click();
```

### Opción 2: Registrar usuario manualmente

Si solo necesitas tu usuario principal:

1. Ve a la página de registro
2. Crea el usuario:
   - **Username**: `Panchita's Catering`
   - **Email**: `cotoala@gmail.com`
   - **Contraseña**: La que tú quieras (recuérdala)
   - **Fecha de nacimiento**: `1982-08-30`

---

## 🎯 VENTAJAS DE POSTGRESQL

✅ **Datos permanentes** - NUNCA se borran
✅ **Una sola base de datos** - No hay duplicaciones
✅ **Completamente gratis** - Plan free de Render
✅ **500 MB de almacenamiento** - Suficiente para miles de registros
✅ **Sin limite de tiempo** - Funciona indefinidamente
✅ **Backups automáticos** - Render hace respaldos diarios

---

## 📊 ESTADO ACTUAL

- ✅ Código actualizado para PostgreSQL
- ✅ Compatibilidad con SQLite (desarrollo local)
- ✅ render.yaml configurado para crear DB automáticamente
- ✅ Requirements actualizado con psycopg2
- ⏳ Pendiente: Desplegar en Render

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "No se pudo conectar a la base de datos"
- Verifica que la variable `DATABASE_URL` esté configurada en Render
- Asegúrate de que la base de datos PostgreSQL esté activa (estado "Available")

### Error: "relation does not exist"
- Las tablas no se han creado
- Reinicia el servidor backend en Render
- Verifica los logs del servidor

### Los datos se siguen borrando
- Confirma que estás usando la URL de producción: `https://aplicacion-mi.vercel.app`
- NO uses localhost, los datos en local son diferentes

---

## 📞 SIGUIENTE PASO

**ACCIÓN REQUERIDA**: 
1. Sube los cambios a GitHub (Paso 1)
2. Crea la base de datos PostgreSQL en Render (Paso 2)
3. Configura DATABASE_URL (Paso 3)
4. ¡Listo! Los datos persisten para siempre
