import socket
import pyautogui
import time

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "0.0.0.0"
UDP_PORT = 50000

# --- PARÁMETROS DE ARQUITECTURA ---
SENSITIVITY = 8.0        # Aumentado para facilitar el movimiento
SMOOTH_FACTOR = 0.3      # Menos suavizado para reducir latencia percibida
DEADZONE = 0.05          # Zona muerta mínima para evitar que se quede estático
SHAKE_THRESHOLD = 30.0   # Umbral para minimizar
SCROLL_LIMIT = 4.0       # Inclinación para scroll
GYRO_CLICK_LIMIT = 15.0  # Giro rápido para clic

# Estado global
prev_dx, prev_dy = 0, 0
last_action = 0

pyautogui.FAILSAFE = False

def start_server():
    global prev_dx, prev_dy, last_action
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False) # Modo no bloqueante para eliminar el delay acumulado
    
    print(f"Servidor Optimizado Activo. Escuchando en puerto {UDP_PORT}...")

    try:
        while True:
            try:
                # 1. LIMPIEZA DE BÚFER: Leer paquetes hasta el último disponible
                data = None
                while True:
                    try:
                        data, _ = sock.recvfrom(1024)
                    except BlockingIOError:
                        break
                
                if not data:
                    continue

                line = data.decode('utf-8').strip()
                parts = line.split(',')
                
                if len(parts) >= 4:
                    # HyperIMU suele enviar: [ID, X, Y, Z]
                    ax, ay, az = float(parts[1]), float(parts[2]), float(parts[3])
                    now = time.time()

                    # 2. FUNCIÓN CLIC (Giroscopio - Si el ID corresponde)
                    if abs(ax) > GYRO_CLICK_LIMIT and now - last_action > 0.5:
                        pyautogui.click()
                        print("[EVENTO] Clic ejecutado")
                        last_action = now
                        continue

                    # 3. FUNCIÓN MINIMIZAR
                    if (abs(ax) + abs(ay) + abs(az)) > SHAKE_THRESHOLD:
                        if now - last_action > 2:
                            pyautogui.hotkey('ctrl', 'alt', 'd')
                            print("[EVENTO] Escritorio mostrado (Minimizar)")
                            last_action = now
                        continue

                    # 4. FUNCIÓN SCROLL
                    if abs(ay) > SCROLL_LIMIT and now - last_action > 0.3:
                        direction = -1 if ay > 0 else 1
                        pyautogui.scroll(direction * 4)
                        print(f"[EVENTO] Scroll {'Abajo' if direction < 0 else 'Arriba'}")
                        last_action = now
                        continue

                    # 5. MOVIMIENTO DEL MOUSE
                    if abs(ax) > DEADZONE or abs(ay) > DEADZONE:
                        target_dx = -ay * SENSITIVITY
                        target_dy = -ax * SENSITIVITY
                        
                        actual_dx = (prev_dx * (1 - SMOOTH_FACTOR)) + (target_dx * SMOOTH_FACTOR)
                        actual_dy = (prev_dy * (1 - SMOOTH_FACTOR)) + (target_dy * SMOOTH_FACTOR)

                        pyautogui.moveRel(int(actual_dx), int(actual_dy))
                        prev_dx, prev_dy = actual_dx, actual_dy

            except (ValueError, IndexError):
                continue
            except Exception:
                continue

    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()