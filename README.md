# Mouse Virtual No Convencional (IMU-UDP Server)

Este proyecto implementa un periférico de entrada no convencional para **Linux (Ubuntu Mate)** que utiliza los sensores inerciales de un smartphone para controlar el cursor del sistema operativo. La comunicación se realiza mediante el protocolo **UDP** de baja latencia, permitiendo una interacción fluida en tiempo real.

## Características Principales

- **Control de Movimiento**: Uso del sensor *Linear Acceleration* para un desplazamiento preciso del cursor sin interferencia de la gravedad.
- **Fusión de Sensores**: Integración de Acelerómetro y Giroscopio para distinguir entre movimiento, clics y gestos.
- **Gestos Avanzados**:
  - **Shake-to-Minimize**: Agitado vectorial para minimizar/restaurar todas las ventanas (`Ctrl + Alt + D`).
  - **Tilt-Scroll**: Inclinación lateral para desplazamiento vertical (Scroll) dinámico.
  - **Air-Click**: Rotación rápida de muñeca para ejecutar clics izquierdos.
- **Arquitectura de Baja Latencia**: Servidor de sockets no bloqueantes que elimina el lag acumulado mediante el vaciado agresivo del búfer de red.

## Requisitos del Sistema

### Hardware
- PC con **Ubuntu Mate** (o cualquier distribución Linux con servidor X11).
- Smartphone Android/iOS con la aplicación **HyperIMU**.
- Red Local (Wi-Fi) compartida entre ambos dispositivos.

### Software (Servidor)
- Python 3.12+
- Dependencias de Python:
  ```bash
  sudo apt-get install python3-tk python3-dev
  pip install pyautogui
