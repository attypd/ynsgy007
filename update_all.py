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
TIMEOUT = 0.8

def check_port_alive(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return str(port) if s.connect_ex((TARGET_HOST, port)) == 0 else None
    except: return None

def scan_for_ports():
    print("正在探测最新有效端口...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_port_alive, SCAN_PORTS)
    return [p for p in results if p]

def update_live():
    valid_ports = []
    php_content = ""
    
    # 1. 抓取 PHP 内容并提取其中正在使用的端口
    try:
        resp = requests.get(PHP_URL, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
            found = re.findall(r'url\.cdnhs\.store:(\d+)', php_content)
            for p in set(found):
                if check_port_alive(int(p)): valid_ports.append(p)
    except: pass

    # 2. 应急：若 PHP 端口不通，全量扫描
    if not valid_ports: valid_ports = scan_for_ports()
    if not valid_ports: return
    
    main_port = valid_ports[0]
    final_output = []
    has_private_in_php = False

    # 3. 逐行处理 PHP 内容，确保顺序与源完全同步
    if php_content:
        for line in php_content.split('\n'):
            line = line.strip()
            if not line: continue
            
            # 识别分组行：转换“分类名称：”为“#genre#”
            if "分类名称" in line:
                genre_name = line.replace("分类名称：", "").replace("分类名称:", "").strip()
                if not genre_name: continue
                # 如果是私密分组，标记已存在
                if "私密" in genre_name:
                    has_private_in_php = True
                    genre_name = f"{genre_name}_1818" if "_1818" not in genre_name else genre_name
                final_output.append(f"\n{genre_name}#genre#")
            
            # 识别频道行：同步源并修正端口
            elif "," in line and "http" in line:
                # 保持原样输出，仅替换端口
                line = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", line)
                final_output.append(line)

    # 4. 只有在 PHP 彻底没有私密分组时，才追加仓库里的 my20262.6.txt
    if not has_private_in_php and os.path.exists(PRIVATE_FILE):
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            p_data = f.read().strip()
            if p_data:
                # 端口同步替换
                p_data = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", p_data)
                final_output.append("\n" + p_data)

    # 5. 写入 total_live.txt
    with open("total_live.txt", "w", encoding="utf-8") as f:
        # 过滤掉空行，保持紧凑的标准 TXT 格式
        f.write("\n".join([l for l in final_output if l.strip()]))
    print(f"同步完成，已应用最新端口: {main_port}")

if __name__ == "__main__":
    update_live()
