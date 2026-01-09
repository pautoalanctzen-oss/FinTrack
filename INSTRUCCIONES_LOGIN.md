# Instrucciones de Login - Panchita's Catering

## Acceso a la Aplicación

### URL Correcta
- **Producción**: https://aplicaci-n-mi.vercel.app
- **Alternativa Desarrollo**: http://127.0.0.1:8000 (si el backend local está ejecutándose)

### Credenciales

```
Usuario: Panchita's Catering
Contraseña: Panchitas2026
```

---

## Solución de Problemas

### Error: "Credenciales inválidas"

#### Posible Causa 1: Escribiste el usuario incorrectamente
- **Importante**: El nombre de usuario es exactamente: `Panchita's Catering` (con el apóstrofo)
- Verifica que hayas escrito correctamente incluyendo la tilde y el apóstrofo

#### Posible Causa 2: La contraseña tiene mayúsculas/minúsculas diferentes
- **Correcto**: `Panchitas2026` (con "P" mayúscula, "2026" números)
- **Incorrecto**: `panchitas2026` (P minúscula)

#### Posible Causa 3: El navegador guarda credenciales antiguas
**Solución**:
1. Abre la consola del navegador (F12 o Ctrl+Shift+I)
2. Ve a la pestaña "Application" / "Storage"
3. Limpia el localStorage:
   ```javascript
   localStorage.clear()
   sessionStorage.clear()
   ```
4. Recarga la página (F5)
5. Intenta login nuevamente

#### Posible Causa 4: Problemas de caché del navegador
**Solución**:
1. Presiona `Ctrl+Shift+Supr` (Windows) o `Cmd+Shift+Supr` (Mac)
2. Selecciona "Borrar datos de navegación"
3. Elige el rango "Todo el tiempo"
4. Marca "Cookies y otros datos del sitio" y "Archivos almacenados en caché"
5. Haz clic en "Borrar datos"
6. Intenta login nuevamente

#### Posible Causa 5: El backend de Render está dormido (cold start)
**Síntoma**: Tarda mucho en responder o se agota el tiempo de espera

**Solución**:
1. Espera 10-15 segundos para que Render despierte el servidor
2. Intenta nuevamente
3. Si sigue fallando, accede a: https://aplicaci-n-mi.onrender.com/health
   - Si ves `{"status": "healthy", ...}`, el servidor está activo

---

## Verificación del Backend

Para confirmar que el servidor está funcionando:

```
URL: https://aplicaci-n-mi.onrender.com/health

Respuesta esperada:
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

Si ves este mensaje, el backend está bien. El problema está en otra parte.

---

## Verificación de la Base de Datos

El usuario "Panchita's Catering" debe existir en la base de datos con:
- **Email**: cotoala@gmail.com
- **Username**: Panchita's Catering
- **Birthdate**: 1982-08-30

---

## Pasos para Hacer Login Correctamente

1. **Abre el navegador** en https://aplicaci-n-mi.vercel.app
2. **Espera** a que cargue completamente
3. **Escribe el usuario**: `Panchita's Catering` (exactamente así)
4. **Escribe la contraseña**: `Panchitas2026`
5. **Presiona "Iniciar Sesión"**
6. **Espera** a que procese (puede tardar 3-5 segundos en Render)
7. **Si todo está bien**, verás el mensaje "Inicio de sesión exitoso" en verde
8. **Se redirigirá automáticamente** al dashboard

---

## Si Aún No Funciona

1. **Abre la consola** (F12)
2. **Ve a la pestaña "Console"**
3. **Intenta login** y **copia los logs** que aparezcan
4. **Comparte esos logs** para ayudarte a diagnosticar

---

## Datos Migrados Disponibles

Una vez dentro del sistema, verás:

| Elemento | Cantidad |
|----------|----------|
| Registros | 290+ |
| Obras | 10 |
| Clientes | 30 |
| Productos | 2 |

Todos los datos de Panchita's Catering están disponibles en el dashboard.
