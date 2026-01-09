# 🚀 GUÍA RÁPIDA - INICIO DEL SERVIDOR

## Para Iniciar el Servidor (RECOMENDADO)

### Opción 1: Doble Click 🖱️
Simplemente haz doble click en:
```
start_server.bat
```

### Opción 2: Desde Terminal
```cmd
start_server.bat
```

---

## ¿Qué Hace Esto?

✅ Inicia el servidor en modo desarrollo
✅ Habilita hot-reload (cambios automáticos)
✅ Supervisión automática activada
✅ Si el servidor se cae, se reinicia solo
✅ Guarda logs en `backend.log`

---

## URLs Importantes

- 🌐 **Aplicación**: http://127.0.0.1:8000
- 💚 **Health Check**: http://127.0.0.1:8000/health
- 📊 **Status**: http://127.0.0.1:8000/api/status

---

## Usuario Demo

- **Usuario**: demo
- **Contraseña**: Demo1234

---

## Para Detener el Servidor

Presiona `Ctrl + C` en la terminal

---

## Ver Logs

```powershell
# Ver en tiempo real
Get-Content backend.log -Wait

# Ver últimas líneas
Get-Content backend.log -Tail 50
```

---

## ¿Problemas?

1. Revisa `backend.log`
2. Verifica http://127.0.0.1:8000/health
3. Asegúrate de que no hay otro proceso en el puerto 8000

---

## Producción

Para modo producción (sin hot-reload):
```cmd
start_server_production.bat
```

---

## ¡Eso es Todo! 🎉

El servidor está protegido contra caídas y se recupera automáticamente.
