# Prueba  — Growth Engineer (Xepelin)

Aplicación web que permite visualizar y editar tasas desde un **Google Sheet**, 
enviando una notificación automática por correo cuando una tasa es modificada.  
El sistema está construido con **Flask**, **Google Sheets API** y **Zapier**, 
y desplegado en **Railway**.

---

##  Descripción General

La aplicación tiene dos partes:

1. **Frontend (HTML/JS):**
   - Login básico (usuario: `admin`, contraseña: `123`).
   - Dashboard con una tabla editable que muestra las tasas desde un Google Sheet.
   - Cada fila permite modificar una tasa y enviarla al backend.

2. **Backend (Flask + Railway):**
   - Expone un endpoint `/api/guardar` que recibe la actualización.
   - Notifica el cambio mediante un webhook de **Zapier**.
   - Actualiza la tasa correspondiente en el **Google Sheet**.
   - Devuelve un JSON con el resultado (`ok`, `msg`).

---

##  Credenciales de Prueba

- **Usuario:** `admin`  
- **Contraseña:** `123`


El login es una autenticación **local y minimalista** creada solo para fines de la prueba técnica.  
No utiliza base de datos ni backend. 



