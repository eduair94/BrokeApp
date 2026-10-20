# Actuación en clase - GitHub Actions y Docker (DEMO)

## Objetivo

Diagnosticar y corregir los problemas en un pipeline de CI/CD existente que utiliza GitHub Actions y Docker para conseguir un flujo de integración y despliegue funcional.

## Contexto

Se te ha entregado un repositorio con una aplicación web simple y un pipeline de CI/CD implementado con GitHub Actions y Docker. Sin embargo, el pipeline tiene varios problemas que debes identificar y corregir para que funcione correctamente.

## Problemas a resolver

> **Resuelto.** Causa, corrección y verificación de cada problema: [SOLUCION.md](SOLUCION.md).

El pipeline actual tiene los siguientes componentes, pero ninguno funciona correctamente:

### 1. Integración Continua

- [x] Trigger desde rama main
- [x] Versión de Python incorrecta
- [x] Nombre del archivo de dependencias incorrecto
- [x] Directorio de tests incorrecto

### 2. Docker

- [x] Imagen actualizada de Python
- [x] Revisar ruta de copia de requirements.txt
- [x] Corregir error al ejecutar la aplicación

### 3. APP / Testing

> **Nota:** el archivo `app/main.py` no debe modificarse. Los demás archivos deben corregirse para que sean consistentes con su implementación.

- [x] Solucionar comportamiento del test
- [x] Nombre del endpoint de check incorrecto
- [x] Valor de respuesta incorrecto

## Estructura del repositorio

```
├── app/                    # Código fuente de la aplicación
│   ├── main.py             # Aplicación simple en Python
│   └── test_main.py        # Pruebas unitarias
├── .github/
│   └── workflows/          # Contiene el workflow ci-cd.yml (tiene errores)
├── Dockerfile              # Dockerfile 
├── README.md               # Este archivo
└── requirements.txt        # Dependencias de la aplicación
```

## Evaluación

Tu solución se evaluará automáticamente según los siguientes criterios:
1. El pipeline se ejecuta correctamente sin errores
2. Todos los problemas identificados han sido corregidos
3. La imagen Docker se construye y publica correctamente
4. Las pruebas automáticas se ejecutan y pasan
5. El flujo implementa las prácticas de seguridad requeridas

Recibirás puntos por cada problema que identifiques y corrijas correctamente.

## Entrega

Para completar el ejercicio:
1. Clona el repositorio generado
2. Identifica y corrige todos los problemas en los diferentes archivos del repo
3. Haz commit y push de tus cambios
4. Verifica que el pipeline funcione correctamente en la pestaña "Actions"

¡Buena suerte!
