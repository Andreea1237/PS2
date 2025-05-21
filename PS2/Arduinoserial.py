# serial_monitor.py
import serial
import time
import requests

ser = serial.Serial("COM4", 9600, timeout=1)  # Asigură-te că portul este corect
time.sleep(2)  # Timp pentru inițializarea conexiunii seriale

last_message = "NULL"

while True:
    # ✅ Citește toate liniile disponibile din bufferul serial
    while ser.in_waiting:
        try:
            line = ser.readline().decode(errors='ignore').strip()
        except Exception as e:
            print(f"Eroare la citirea din serial: {e}")
            continue

        if not line:
            continue

        print(f"[SERIAL] Primit: {line}")

        # ✅ Temperatura
        if line.startswith("TEMP:"):
            temperature = line.split(":")[1]
            print(f"Temperatura: {temperature}°C")
            try:
                requests.post("http://127.0.0.1:5000/update_temperature", data={"temperature": temperature})
            except Exception as e:
                print(f"Eroare trimitere temperatură: {e}")

        # ✅ Inundație
        elif line == "FLOOD_DETECTED":
            print("Inundație detectată!")
            try:
                requests.post("http://127.0.0.1:5000/detect_flood")
            except Exception as e:
                print(f"Eroare trimitere inundație: {e}")

    # ✅ Trimite stare LED către Arduino
    try:
        led_state = requests.get("http://127.0.0.1:5000/get_led").text.strip()
        if led_state == "1":
            ser.write(b"LED_ON\n")
        else:
            ser.write(b"LED_OFF\n")
    except Exception as e:
        print(f"Eroare stare LED: {e}")

    # ✅ Trimite mesaj nou dacă există
    try:
        message = requests.get("http://127.0.0.1:5000/get_message").text.strip()
        if message != "NULL" and message != last_message:
            print(f"Mesaj nou: {message}")
            ser.write((message + "\n").encode())
            last_message = message
    except Exception as e:
        print(f"Eroare mesaj: {e}")

    time.sleep(1.5)  # Ajustează dacă e nevoie
