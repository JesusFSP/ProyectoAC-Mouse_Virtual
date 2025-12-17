from flask import Flask, request
import pyautogui
import math

app = Flask(__name__)

# --- PARÁMETROS DE ARQUITECTURA AVANZADA ---
SENSITIVITY = 40.0
SMOOTH_FACTOR = 0.25
# Umbral para detectar inclinación extrema (Modo Scroll)
SCROLL_THRESHOLD = 7.0 
# Umbral de aceleración para Clic (Golpe seco en Z)
ACCEL_CLICK_Z = 13.0

# Estado del sistema
curr_x, curr_y = 0, 0
pyautogui.FAILSAFE = False

def process_gesture(ax, ay, az):
    global curr_x, curr_y
    
    # 1. MODO CLICK: Detección de impulso en el eje Z (Mundo Real -> Digital) 
    if az > ACCEL_CLICK_Z:
        pyautogui.click()
        return "CLICK"

    # 2. MODO SCROLL: Si el teléfono se inclina demasiado hacia adelante [cite: 1198]
    if ay > SCROLL_THRESHOLD:
        pyautogui.scroll(-5)
        return "SCROLL DOWN"
    elif ay < -SCROLL_THRESHOLD:
        pyautogui.scroll(5)
        return "SCROLL UP"

    # 3. MODO MOUSE: Movimiento fluido con filtro de media móvil
    target_dx = -ax * SENSITIVITY
    target_dy = -ay * SENSITIVITY
    
    # Suavizado de señal (Interpolación lineal)
    curr_x = (curr_x * (1 - SMOOTH_FACTOR)) + (target_dx * SMOOTH_FACTOR)
    curr_y = (curr_y * (1 - SMOOTH_FACTOR)) + (target_dy * SMOOTH_FACTOR)
    
    pyautogui.moveRel(int(curr_x), int(curr_y), duration=0.01)
    return "MOVE"

@app.route('/data', methods=['POST'])
def handle_sensors():
    data = request.get_json()
    if data and 'payload' in data:
        for entry in data['payload']:
            if entry.get('name') == 'accelerometer':
                v = entry.get('values', {})
                # Sensor Logger entrega m/s^2
                status = process_gesture(v.get('x', 0), v.get('y', 0), v.get('z', 0))
    return "OK", 200

if __name__ == '__main__':
    # Ejecución mono-hilo para evitar colisiones en el driver de video 
    app.run(host='0.0.0.0', port=50000, threaded=False)