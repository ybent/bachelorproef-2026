import csv
import os
import sys
import time
import psutil

# Supported target IDS engines
TARGET_ENGINES = ["suricata", "zeek"]
SAMPLE_INTERVAL = 1.0


def get_target_processes(engine_names):
    """Finds and returns persistent psutil.Process objects matching any target engine name."""
    procs = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            proc_name = proc.info["name"]
            if proc_name and any(
                engine.lower() in proc_name.lower() for engine in engine_names
            ):
                procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def main():
    # 1. Parse Output File Parameter
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "ids_metrics.csv"
        print(f"[*] No output file specified. Defaulting to '{output_file}'.")

    # Ensure output directory exists if a path like /output/file.csv was passed
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 2. Find Active IDS Processes (Suricata or Zeek)
    procs = get_target_processes(TARGET_ENGINES)
    if not procs:
        print(
            f"[!] Error: No active processes found for engines: {', '.join(TARGET_ENGINES)}"
        )
        sys.exit(1)

    # Group detected process names for clear output logging
    detected_names = set(p.name() for p in procs)
    pids = [p.pid for p in procs]

    # 3. Initialize CPU measurement baseline for each process
    for p in procs:
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    print(
        f"[*] Monitoring Active IDS: {', '.join(detected_names)} (PIDs: {pids})"
    )
    print(f"[*] Writing telemetry to: {output_file}")
    time.sleep(1)  # Baseline time interval window

    # 4. Monitoring Loop
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Timestamp_Sec", "CPU_Percent", "RAM_MB", "RAM_Percent"]
        )

        start_time = time.time()
        try:
            while True:
                # Filter out any terminated processes
                procs = [p for p in procs if p.is_running()]
                if not procs:
                    print("\n[!] All monitored IDS processes have terminated.")
                    break

                total_cpu = 0.0
                total_ram_mb = 0.0
                total_ram_percent = 0.0

                for proc in procs:
                    try:
                        total_cpu += proc.cpu_percent(interval=None)
                        mem_info = proc.memory_info()
                        total_ram_mb += mem_info.rss / (1024 * 1024)
                        total_ram_percent += proc.memory_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                elapsed_time = round(time.time() - start_time, 2)

                writer.writerow(
                    [
                        elapsed_time,
                        round(total_cpu, 2),
                        round(total_ram_mb, 2),
                        round(total_ram_percent, 2),
                    ]
                )
                file.flush()

                time.sleep(SAMPLE_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n[*] Monitoring stopped. Data saved to '{output_file}'.")

if __name__ == "__main__":
    main()