# 🚀 Base de Datos Permanente: PostgreSQL con Neon (Gratis y Duradero)

## ⚠️ Problema
- En Render Free, el almacenamiento del contenedor es efímero: **SQLite se borra** en redeploys o reinicios.
- Necesitas persistencia real sin pagar y sin fecha de caducidad.

## ✅ Solución Recomendada: Neon (Plan Free)
Neon ofrece PostgreSQL administrado con **persistencia duradera**, **SSL**, y **autosleep**. El plan gratuito mantiene tus datos (no expiran) y es perfecto para este proyecto.

---

## 📋 Pasos de Configuración (≈10 minutos)

### Paso 1: Crear la base en Neon
1. Ve a https://neon.tech → Sign up.
2. Create Project:
   - **Project name**: `fintrack`
   - **Region**: cercana a Oregon (p. ej., `aws-us-west-2`).
   - **Database**: `fintrack_db2`
   - **Role/User**: `fintrack_user1`
3. Copia el **Connection string** tipo `postgres://USER:PASSWORD@HOST/fintrack_db2`.
4. Añade `?sslmode=require` al final: `.../fintrack_db2?sslmode=require`.

### Paso 2: Configurar el backend en Render
1. En tu servicio backend, abre **Environment**.
2. Agrega/actualiza la variable:
   - **Key**: `DATABASE_URL`
   - **Value**: el connection string de Neon con `?sslmode=require`.
3. Guarda y **redeploy** el servicio.

### Paso 3: Verificar salud
1. Abre `/health` de tu backend.
2. Logs deben indicar: PostgreSQL activo y `DATABASE_URL` detectado.

### Paso 4: Importar tus datos
Opciones:
- Desde la UI de la app (importar respaldo).
- O vía API con el archivo en `backups/api_snapshot_2026-01-09.json`.

---

## 🔧 Notas de Operación
- Neon Free es **sin costo** y **sin expiración**; puede entrar en "autosleep" tras inactividad, la **primera conexión** tarda unos segundos.
- Rendimiento adecuado para tráfico bajo/medio; si necesitas más, puedes subir de plan después.

---

## 🆘 Troubleshooting
**No conecta / error SSL**
- Verifica que el `DATABASE_URL` termine con `?sslmode=require`.
- Confirma credenciales y que el proyecto Neon esté activo.

**"relation does not exist"**
- Ejecuta nuevamente la inicialización del esquema (el backend la crea al iniciar) o haz un redeploy.

**Sigue usando SQLite**
- Asegúrate de haber definido `DATABASE_URL` en Render y que los logs no muestren modo SQLite.

---

## 📊 Estado / Compatibilidad
- Backend preparado para conmutar entre SQLite y PostgreSQL automáticamente según `DATABASE_URL`.
- `psycopg2-binary` actualizado para compatibilidad.
- Frontend listo; no requiere cambios.

---

## ✅ Checklist rápido
- [ ] Neon creado y connection string copiado.
- [ ] `DATABASE_URL` configurado en Render con `?sslmode=require`.
- [ ] `/health` OK y logs muestran PostgreSQL.
- [ ] Respaldo importado.

Con esto, tus datos **no se pierden** y **no tienes que pagar**.
