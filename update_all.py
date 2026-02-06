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
            return str(port) if s.connect_ex((TARGET_HOST, port)) == 0 else None
    except: return None

def scan_for_ports():
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_port_alive, SCAN_PORTS)
    return [p for p in results if p]

def update_live():
    valid_ports = []
    php_content = ""
    
    # 1. 抓取与端口探测
    try:
        resp = requests.get(PHP_URL, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
            found = re.findall(r'url\.cdnhs\.store:(\d+)', php_content)
            for p in set(found):
                if check_port_alive(int(p)): valid_ports.append(p)
    except: pass

    if not valid_ports: valid_ports = scan_for_ports()
    if not valid_ports: return
    
    main_port = valid_ports[0]
    new_lines = []
    has_private = False

    # 2. 暴力处理逻辑：不管 PHP 返回什么，强行转换分组
    if php_content:
        for line in php_content.split('\n'):
            line = line.strip()
            if not line: continue
            
            # 兼容性匹配：只要包含“分类”或者以“香港”、“我的”开头，就转为分组
            if "分类名称" in line or line.startswith("香港") or line.startswith("我的"):
                genre_name = line.replace("分类名称：", "").replace("分类名称:", "").strip()
                if "私密" in genre_name: 
                    has_private = True
                    new_lines.append(f"\n{genre_name}_1818#genre#")
                else:
                    new_lines.append(f"\n{genre_name}#genre#")
            
            # 频道链接处理
            elif "," in line:
                # 统一替换端口并确保格式为：频道名,链接
                line = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", line)
                new_lines.append(line)

    # 3. 强制补全私密分组 (读取你的 my20262.6.txt)
    if not has_private and os.path.exists(PRIVATE_FILE):
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            p_data = f.read()
            # 统一替换补全文件里的端口
            p_data = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", p_data)
            # 确保私密分组带有 1818 密码后缀
            if "私密频道" in p_data and "#genre#" not in p_data:
                new_lines.append("\n私密频道_1818#genre#")
            new_lines.append(p_data.strip())

    # 4. 最终写入 (确保不留空行)
    final_output = "\n".join([l for l in new_lines if l.strip()])
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

if __name__ == "__main__":
    update_live()
