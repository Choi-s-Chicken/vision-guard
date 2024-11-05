import os
import socket
import requests
import json
from ipaddress import ip_network, ip_interface
from tqdm import tqdm
import netifaces

def get_local_ip():
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if ip.startswith('192.168'):
                    return ip
    return None

hostname = socket.gethostname()
local_ip = get_local_ip()

# Convert local_ip to a network address with host bits set to zero
NETWORK_RANGE = str(ip_interface(f"{local_ip}/24").network)
PORT = 80
EXPECTED_RESPONSE = {
    "is_vgdevice": True
}

def find_vgdevice():
    ip_list = list(ip_network(NETWORK_RANGE))
    for ip in tqdm(ip_list, desc="비전가드 제품을 찾고 있습니다 . . ."):
        url = f"http://{ip}:{PORT}/vgdevicegetinfo"
        try:
            response = requests.get(url, timeout=0.1)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_vgdevice") == True:
                    print(f"제품을 찾았습니다. http://{ip}")
                    print(f"모델 이름: {data.get('model', '정보 없음')}")
                    return ip
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            continue
    
    print("제품을 찾을 수 없습니다. 제품이 동일한 네트워크에 연결되어있나요?")
    return None

if __name__ == "__main__":
    os.system("cls")
    while True:
        print("[비전가드 제품 찾기 마법사]")
        print(f"{hostname} {local_ip}")
        print(end="\n")
        print("1. 비전가드 제품 접속 주소 찾기")
        print("2. 내 IP 주소 갱신")
        print("3. 종료")
        choice = input("선택: ")
        print(end="\n")
        
        if choice == "1":
            find_vgdevice()
            os.system("pause")
        elif choice == "2":
            print("내 IP 주소를 갱신하고 있습니다 . . .")
            local_ip = get_local_ip()
        elif choice == "3":
            print("비전가드 제품 찾기 마법사를 종료합니다.")
            exit(0)
            
        os.system("cls")