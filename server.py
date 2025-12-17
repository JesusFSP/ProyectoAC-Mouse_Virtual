import socket
import pyautogui
import time

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "0.0.0.0"
UDP_PORT = 50000

# --- PARÁMETROS DE ARQUITECTURA ---
SENSITIVITY = 15.0     # Bajamos sensibilidad 
SMOOTH_FACTOR = 0.15   # Suavizado
SHAKE_THRESHOLD = 45.0 # Subimos el umbral para que no se minimice solo
SCROLL_THRESHOLD = 10.0 # Inclinación para el scroll
GYRO_CLICK_LIMIT = 8.0 # Rotación para clic

# Variables de estado
curr_x, curr_y = 0, 0
prev_dx, prev_dy = 0, 0
last_action_time = 0

pyautogui.FAILSAFE = False

def start_server():
    global last_action_time, prev_dx, prev_dy
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Servidor UDP listo. Escuchando HyperIMU en puerto {UDP_PORT}")

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            line = data.decode('utf-8').strip()
            parts = line.split(',')
            
            # Buscamos el acelerómetro.
            if len(parts) >= 4:
                try:
                    ax = float(parts[1])
                    ay = float(parts[2])
                    az = float(parts[3])
                    now = time.time()

                    # 1. DETECCIÓN DE AGITADO (Minimizar)
                    accel_total = abs(ax) + abs(ay) + abs(az)
                    if accel_total > SHAKE_THRESHOLD:
                        if now - last_action_time > 2:
                            pyautogui.hotkey('ctrl', 'alt', 'd')
                            print("[EVENTO] Sistema minimizado (Agitado detectado)")
                            last_action_time = now
                        continue

                    # 2. DETECCIÓN DE SCROLL (Inclinación lateral Y)
                    if ay > SCROLL_THRESHOLD:
                        pyautogui.scroll(-2)
                        print("[EVENTO] Scroll Abajo")
                        continue
                    elif ay < -SCROLL_THRESHOLD:
                        pyautogui.scroll(2)
                        print("[EVENTO] Scroll Arriba")
                        continue

                    # 3. MOVIMIENTO DEL MOUSE CON SUAVIZADO
                    # Calculamos el objetivo
                    target_dx = -ay * SENSITIVITY
                    target_dy = -ax * SENSITIVITY

                    # Filtro de media móvil (Suavizado)
                    actual_dx = (prev_dx * (1 - SMOOTH_FACTOR)) + (target_dx * SMOOTH_FACTOR)
                    actual_dy = (prev_dy * (1 - SMOOTH_FACTOR)) + (target_dy * SMOOTH_FACTOR)

                    # Movimiento relativo
                    if abs(actual_dx) > 0.5 or abs(actual_dy) > 0.5:
                        pyautogui.moveRel(int(actual_dx), int(actual_dy), duration=0.01)
                    
                    prev_dx, prev_dy = actual_dx, actual_dy

                except (ValueError, IndexError):
                    continue

    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()