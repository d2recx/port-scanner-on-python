import time

import argparse
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

# 1. Создаем объект блокировки (общий для всех потоков)
print_lock = threading.Lock()
open_ports_count = 0

def scan_port(target_host, target_port):

    global args
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)


    try:
        result = s.connect_ex((target_host, target_port))

        if result == 0:
            with print_lock:
                global open_ports_count
                open_ports_count += 1
                print(f"[+] Порт {target_port}: ОТКРЫТ")

                with open("scan_report.txt", "a", encoding="utf-8") as f:
                    f.write(f"[+] Порт {target_port}: ОТКРЫТ\n")
    except socket.error:
        pass
    finally:
        s.close()

def scan_ports(target_host, ports):
    global open_ports_count
    print(f"\n🔍 Запуск многопоточного сканирования: {target_host}\n")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        for port in ports:
            executor.submit(scan_port, target_host, port)

    end_time = time.time()

    eplased_time = end_time - start_time

    print(f"\n Scan is over on {eplased_time: .2f} sec")
    print(f"Most open: {open_ports_count}")
    print("Save a result time on scan_targer.txt")
    with open("scan_report.txt", "a", encoding="utf-8") as f:
        f.write(f"Most open: {open_ports_count}")
        f.write(f"\n Scan is over on {eplased_time: .2f} sec")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Многопоточный TCP-сканер с блокировкой вывода.")
    parser.add_argument("-t", "--target", required=True, help="Целевой IP-адрес")
    parser.add_argument("-p", "--ports", required=True, help="Порт или диапазон (например, 1-100)")
    parser.add_argument("-o", "--timeout", required=True, type=float, help="Record a timeout")

    args = parser.parse_args()

    try:
        if "-" in args.ports:
            start, end = args.ports.split("-")
            ports_list = list(range(int(start), int(end) + 1))
        else:
            ports_list = [int(args.ports)]
    except ValueError:
        print("[!] Ошибка: неверный формат портов.")
        exit(1)

    scan_ports(args.target, ports_list)
