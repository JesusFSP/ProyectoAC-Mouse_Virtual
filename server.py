import socket
import pyautogui
import time

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "0.0.0.0"
UDP_PORT = 50000

# --- PARÁMETROS DE ARQUITECTURA ---
SENSITIVITY = 12.0
SMOOTH_FACTOR = 0.5
DEADZONE = 0.05
SHAKE_LIMIT = 35.0      # Umbral para el impacto del agitado
SCROLL_LIMIT = 4.0
GYRO_CLICK_LIMIT = 15.0

# Estado global
prev_dx, prev_dy = 0, 0
last_action_time = 0

pyautogui.FAILSAFE = False

def start_server():
    global prev_dx, prev_dy, last_action_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False) 
    
    print(f"Servidor de Alta Fidelidad Activo en puerto {UDP_PORT}...")

    try:
        while True:
            last_data = None
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                    last_data = data
                except BlockingIOError:
                    break
            
            if not last_data:
                time.sleep(0.01)
                continue

            try:
                line = last_data.decode('utf-8').strip()
                parts = line.split(',')
                
                if len(parts) >= 4:
                    ax, ay, az = float(parts[1]), float(parts[2]), float(parts[3])
                    now = time.time()

                    # 1. FUNCIÓN: MINIMIZAR 
                    accel_impact = (ax**2 + ay**2 + az**2)**0.5
                    if accel_impact > SHAKE_LIMIT and now - last_action_time > 2.5:
                        # Ejecutamos el comando 
                        pyautogui.hotkey('ctrl', 'alt', 'd') 
                        print(f"[EVENTO] Minimizado/Restaurado (Impacto: {accel_impact:.2f})")
                        
                        # TRUCO DE ARQUITECTURA: Pequeño delay y clic para recuperar el foco del sistema
                        time.sleep(0.2)
                        pyautogui.press('esc')
                        pyautogui.click(button='left')
                        
                        last_action_time = now
                        continue

                    # 2. FUNCIÓN: CLIC
                    if abs(ax) > GYRO_CLICK_LIMIT and now - last_action_time > 0.6:
                        pyautogui.click()
                        print("[EVENTO] Clic ejecutado")
                        last_action_time = now
                        continue

                    # 3. FUNCIÓN: SCROLL
                    if abs(ay) > SCROLL_LIMIT and now - last_action_time > 0.2:
                        direction = -1 if ay > 0 else 1
                        pyautogui.scroll(direction * 4)
                        print(f"[EVENTO] Scroll {'Abajo' if direction < 0 else 'Arriba'}")
                        last_action_time = now
                        continue

                    # 4. MOVIMIENTO DEL MOUSE
                    if abs(ax) > DEADZONE or abs(ay) > DEADZONE:
                        target_dx = -ay * SENSITIVITY
                        target_dy = -ax * SENSITIVITY
                        actual_dx = (prev_dx * (1 - SMOOTH_FACTOR)) + (target_dx * SMOOTH_FACTOR)
                        actual_dy = (prev_dy * (1 - SMOOTH_FACTOR)) + (target_dy * SMOOTH_FACTOR)
                        pyautogui.moveRel(int(actual_dx), int(actual_dy))
                        prev_dx, prev_dy = actual_dx, actual_dy
                    else:
                        prev_dx, prev_dy = 0, 0

            except (ValueError, IndexError):
                continue

    except KeyboardInterrupt:
        print("\n[INFO] Servidor detenido (Ctrl+C).")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()