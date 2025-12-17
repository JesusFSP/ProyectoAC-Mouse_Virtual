from flask import Flask, request
import pyautogui
import time

app = Flask(__name__)

# --- PARÁMETROS DE ARQUITECTURA ---
SENSITIVITY = 45.0
SMOOTH_FACTOR = 0.2
SCROLL_THRESHOLD = 6.5   # Inclinación para scroll
SHAKE_THRESHOLD = 25.0    # Fuerza para detectar el agitado (minimize)

# Estado global
curr_x, curr_y = 0, 0
last_shake_time = 0

@app.route('/data', methods=['POST'])
def handle_sensors():
    global curr_x, curr_y, last_shake_time
    data = request.get_json()
    
    if data and 'payload' in data:
        for entry in data['payload']:
            if entry.get('name') == 'accelerometer':
                v = entry.get('values', {})
                ax, ay, az = v.get('x', 0), v.get('y', 0), v.get('z', 0)

                # 1. FUNCIÓN: AGITAR PARA MINIMIZAR (Win + D)
                # Si la aceleración total es muy alta, detectamos un agitado
                accel_total = abs(ax) + abs(ay) + abs(az)
                if accel_total > SHAKE_THRESHOLD:
                    now = time.time()
                    if now - last_shake_time > 2: # Evita ejecuciones múltiples (cooldown de 2s)
                        pyautogui.hotkey('winleft', 'd') 
                        print("[EVENTO] ¡Agitado detectado! Ventanas minimizadas.")
                        last_shake_time = now
                    return "SHAKE", 200

                # 2. FUNCIÓN: SCROLL POR INCLINACIÓN
                if ay > SCROLL_THRESHOLD:
                    pyautogui.scroll(-3)
                    return "SCROLL", 200
                elif ay < -SCROLL_THRESHOLD:
                    pyautogui.scroll(3)
                    return "SCROLL", 200

                # 3. MOVIMIENTO NORMAL DEL MOUSE
                target_dx = -ax * SENSITIVITY
                target_dy = -ay * SENSITIVITY
                curr_x = (curr_x * (1 - SMOOTH_FACTOR)) + (target_dx * SMOOTH_FACTOR)
                curr_y = (curr_y * (1 - SMOOTH_FACTOR)) + (target_dy * SMOOTH_FACTOR)
                
                pyautogui.moveRel(int(curr_x), int(curr_y), duration=0.01)

    return "OK", 200

if __name__ == '__main__':
    pyautogui.FAILSAFE = False
    app.run(host='0.0.0.0', port=50000, threaded=False)