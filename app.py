import os
import socket
import requests
import json
from ipaddress import ip_network
from tqdm import tqdm

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

NETWORK_RANGE = f"{local_ip}/24"
PORT = 80
EXPECTED_RESPONSE = {
    "is_vgdevice": True
}

def update_local_ip():
    global NETWORK_RANGE
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    NETWORK_RANGE = f"{local_ip}/24"

def find_vgdevice():
    ip_list = list(ip_network(NETWORK_RANGE))
    for ip in tqdm(ip_list, desc="Searching for VG Device"):
        url = f"http://{ip}:{PORT}/vgdevicegetinfo"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                data = response.json()
                if data == EXPECTED_RESPONSE:
                    print(f"VG Device found at IP: {ip}")
                    return ip
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            continue
    
    print("VG Device not found in the specified network range.")
    return None

if __name__ == "__main__":
    while True:
        print("[비전가드 제품 찾기 마법사]")
        print("1. 비전가드 제품 접속 주소 찾기")
        print("2. 내 IP 주소 갱신")
        print("3. 종료")
        choice = input("선택: ")
        find_vgdevice()
