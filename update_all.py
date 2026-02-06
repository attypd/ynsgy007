import requests
import re
import socket
import os
from concurrent.futures import ThreadPoolExecutor

# 配置信息
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store"
PRIVATE_FILE = "my20262.6.txt"
SCAN_PORTS = [8080] + list(range(40000, 50001))
TIMEOUT = 1.0

def check_port_alive(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            if s.connect_ex((TARGET_HOST, port)) == 0:
                return str(port)
    except:
        pass
    return None

def scan_for_ports():
    print(f"启动应急端口扫描...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_port_alive, SCAN_PORTS)
    return [p for p in results if p]

def update_live():
    valid_ports = []
    php_content = ""
    
    # 1. 抓取 PHP
    try:
        resp = requests.get(PHP_URL, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
            found = re.findall(r'url\.cdnhs\.store:(\d+)', php_content)
            for p in set(found):
                if check_port_alive(int(p)): valid_ports.append(p)
    except:
        print("PHP 接口异常")

    # 2. 端口应急扫描
    if not valid_ports:
        valid_ports = scan_for_ports()

    if not valid_ports: return
    main_port = valid_ports[0]

    # 3. 核心修复：强制格式化分组
    new_lines = []
    has_private = False
    
    if php_content:
        lines = php_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 解决分组不显示的关键：将“分类名称：”转为“#genre#”
            if "分类名称：" in line:
                genre_name = line.replace("分类名称：", "").strip()
                if "私密" in genre_name: 
                    has_private = True
                    new_lines.append(f"{genre_name}_1818#genre#")
                else:
                    new_lines.append(f"{genre_name}#genre#")
            
            # 频道行处理
            elif "," in line and "http" in line:
                line = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", line)
                new_lines.append(line)

    # 4. 补全私密分组
    if not has_private and os.path.exists(PRIVATE_FILE):
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            p_data = f.read()
            # 确保补全的内容里有标准的分组头
            if "#genre#" not in p_data:
                new_lines.append("私密频道_1818#genre#")
            # 统一替换补全文件里的端口
            p_data = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", p_data)
            new_lines.append(p_data.strip())

    # 5. 写入文件
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines).strip())
    print(f"修复完成！最新端口: {main_port}")

if __name__ == "__main__":
    update_live()
