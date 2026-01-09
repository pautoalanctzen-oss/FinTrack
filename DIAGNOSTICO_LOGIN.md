# Diagnóstico de Error de Login "Credenciales Inválidas"

## Status: Backend ✓ Funcionando | Frontend ⏳ En Investigación

El servidor backend **SÍ** autentica correctamente con las credenciales:
- **Usuario**: `Panchita's Catering`
- **Contraseña**: `Panchitas2026`

Pero el formulario de login en el navegador muestra: "Credenciales inválidas"

## Pasos para Diagnosticar el Problema

### 1. Abre la Página de Login
1. Ve a: https://aplicaci-n-mi.vercel.app
2. Presiona **F12** para abrir Herramientas de Desarrollador
3. Ve a la pestaña **Console** (Consola)

### 2. Intenta Login e Ignora Errores
1. En el formulario, ingresa:
   - **Usuario**: `Panchita's Catering`
   - **Contraseña**: `Panchitas2026`
2. Haz clic en "Iniciar Sesión"
3. **NO CIERRES** la consola

### 3. Copia TODOS los Mensajes de la Consola

En la consola verás líneas como:
```
Intentando login con: Panchita's Catering
Enviando petición a: https://aplicaci-n-mi.onrender.com/api/login
Status de respuesta: 200
Datos recibidos: {...}
Tipo de authenticated: ...
```

**Copia TODA la salida de la consola** y dime exactamente qué dice.

### 4. También Busca Errores en Red (Network Tab)
1. Haz clic en la pestaña **Network** (Red)
2. Intenta login de nuevo
3. Busca la petición POST a `/api/login`
4. Haz clic en ella y ve a la pestaña **Response**
5. Copia el JSON que aparece allí

## Lo Que Esperamos Ver

Si todo está bien, en la consola deberías ver:
```
Intentando login con: Panchita's Catering
Enviando petición a: https://aplicaci-n-mi.onrender.com/api/login
Status de respuesta: 200
Datos recibidos: {
  "username": "Panchita's Catering",
  "authenticated": true,
  "message": "Autenticado correctamente"
}
Tipo de authenticated: boolean
Valor de authenticated: true
¿authenticated === true?: true
✓ Autenticación exitosa
Usuario guardado en sessionStorage: Panchita's Catering
Redirigiendo a dashboard.html
```

## Problemas Posibles

### Problema 1: Status !== 200
- El servidor rechaza las credenciales
- **Solución**: Verifica que escribas correctamente la contraseña (mayúsculas/minúsculas importan)

### Problema 2: Status 200 pero `authenticated: false`
- El usuario no existe o la contraseña es incorrecta
- **Solución**: El usuario "Panchita's Catering" DEBE estar registrado exactamente así (con comilla simple)

### Problema 3: Response sin campo `authenticated`
- El backend devuelve algo diferente
- **Solución**: Dime qué JSON devuelve el servidor

### Problema 4: CORS Error (en Network tab)
- El navegador bloquea la petición
- **Solución**: Ya está configurado en el backend, pero podría ser un problema con la URL

## URL Correctas Esperadas

- **Frontend (Vercel)**: https://aplicaci-n-mi.vercel.app
- **Backend (Render)**: https://aplicaci-n-mi.onrender.com

Si ves otras URLs (como `localhost`), el frontend cree que estás en desarrollo local.

---

**Por favor copia la salida de la consola y comparte aquí para que podamos identificar el problema exacto.**
