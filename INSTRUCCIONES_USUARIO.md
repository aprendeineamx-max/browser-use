# Preparación de entorno (Windows) para Fase 2: Motores LAM / Skyvern

## Paso 1: Habilitar WSL2 (si no lo tienes activo)
1. Abre PowerShell **como Administrador**.
2. Ejecuta:
   - **wsl --install**
3. Reinicia Windows si te lo pide.
4. Verifica:
   - **wsl --status**
   - Debe mostrar “Default Version: 2”.

## Paso 2: Instalar y configurar Docker Desktop
1. Descarga Docker Desktop para Windows desde https://www.docker.com/products/docker-desktop/.
2. Instala y, durante el asistente, asegúrate de:
   - Habilitar **WSL2 backend**.
   - Permitir integración con la distro WSL que uses (Ubuntu, etc.).
3. Inicia Docker Desktop y espera a que muestre “Running”.

## Paso 3: Verificación rápida
Ejecuta en PowerShell (no hace falta admin):
- **docker --version**
- **docker run hello-world**
- **docker run mcr.microsoft.com/playwright/python:latest** (valida que puedes bajar la imagen base que usaríamos para motores Playwright/Skyvern).

## Requisitos de recursos
- Al menos **4 GB de RAM libre** y **2 núcleos** disponibles para contenedores con Chromium.
- Virtualización habilitada en BIOS (necesaria para WSL2/Docker).

## Notas y buenas prácticas
- Mantén tu `.env` fuera de la imagen Docker; monta volúmenes o usa variables de entorno al lanzar contenedores.
- Si tu antivirus/firewall bloquea Docker, permite el tráfico saliente para las descargas de imágenes.
