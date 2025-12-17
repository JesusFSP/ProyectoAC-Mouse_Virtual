import socket
import pyautogui
import time

# --- CONFIGURACIÓN DE RED ---
UDP_IP = "0.0.0.0"
UDP_PORT = 50000

# --- PARÁMETROS DE CONTROL ---
SENSITIVITY = 0.5   # Ajusta según HyperIMU
SMOOTH_FACTOR = 0.2
SHAKE_THRESHOLD = 25.0 
last_action_time = 0

# Configuración inicial de PyAutoGUI
pyautogui.FAILSAFE = False

def start_server():
    global last_action_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print(f"Servidor UDP listo. HyperIMU debe apuntar a {UDP_PORT}")

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            line = data.decode('utf-8').strip()
            
            # HyperIMU suele enviar: sensor_id, x, y, z
            # Nota: El formato exacto puede variar según la versión. 
            # Si el mouse no se mueve, revisaremos el print(parts)
            parts = line.split(',')
            
            if len(parts) >= 4:
                try:
                    # Normalmente el acelerómetro es el ID 1 o 3 en HyperIMU
                    ax = float(parts[1])
                    ay = float(parts[2])
                    az = float(parts[3])

                    now = time.time()

                    # 1. FUNCIÓN MINIMIZAR (Atajo para Ubuntu Mate)
                    accel_total = abs(ax) + abs(ay) + abs(az)
                    if accel_total > SHAKE_THRESHOLD:
                        if now - last_action_time > 2:
                            # Atajo correcto para Linux / Ubuntu Mate
                            pyautogui.hotkey('ctrl', 'alt', 'd')
                            print("[EVENTO] Escritorio mostrado (Minimize All)")
                            last_action_time = now
                        continue

                    # 2. MOVIMIENTO DEL MOUSE
                    # Invertimos ejes si es necesario según la orientación
                    dx = int(-ay * SENSITIVITY * 10)
                    dy = int(-ax * SENSITIVITY * 10)
                    
                    pyautogui.moveRel(dx, dy, duration=0.01)

                except ValueError:
                    continue

    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        sock.close()

if __name__ == "__main__":
    start_server()