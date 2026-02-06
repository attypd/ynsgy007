import requests
import re
import socket
import os
from concurrent.futures import ThreadPoolExecutor

# 配置
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store"
PRIVATE_FILE = "my20262.6.txt"
SCAN_PORTS = [8080, 40700, 48370] + list(range(40000, 50001))
TIMEOUT = 0.8

def check_port_alive(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return str(port) if s.connect_ex((TARGET_HOST, int(port))) == 0 else None
    except: return None

def update_live():
    # 1. 探测主服务器当前最快活跃端口 (用于保底和强制跟随)
    print("正在探测主服务器端口...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        scan_results = executor.map(check_port_alive, SCAN_PORTS)
    valid_ports = [r for r in scan_results if r]
    main_port = valid_ports[0] if valid_ports else "48370" # 没扫到则默认一个

    php_content = ""
    try:
        resp = requests.get(PHP_URL, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
    except: pass

    final_output = []
    has_private_in_php = False
    current_genre = ""

    # 2. 处理 PHP 内容
    if php_content:
        for line in php_content.split('\n'):
            line = line.strip()
            if not line: continue
            
            # 分组行处理：强制标准格式 "名称,#genre#"
            if "分类名称" in line:
                current_genre = line.replace("分类名称：", "").replace("分类名称:", "").strip()
                if "私密" in current_genre:
                    has_private_in_php = True
                    # 确保私密分组名包含后缀
                    if "_1818" not in current_genre: current_genre += "_1818"
                final_output.append(f"\n{current_genre},#genre#")
            
            # 频道行处理
            elif "," in line and "http" in line:
                # 检查当前行端口是否存活
                port_match = re.search(r'url\.cdnhs\.store:(\d+)', line)
                if port_match:
                    p = port_match.group(1)
                    # 如果是松视频道或端口不通，强制使用主服务器端口
                    if "松视" in line or p not in valid_ports:
                        line = line.replace(f":{p}", f":{main_port}")
                final_output.append(line)

    # 3. 仓库保底：如果 PHP 里没私密分组，则追加仓库文件
    if not has_private_in_php and os.path.exists(PRIVATE_FILE):
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            p_data = f.read().strip()
            if p_data:
                # 仓库内的源也统一修正为当前主服务器端口
                p_data = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", p_data)
                # 确保追加的分组格式也带有逗号
                p_data = p_data.replace("#genre#", ",#genre#") if ",#genre#" not in p_data else p_data
                final_output.append("\n" + p_data)

    # 4. 写入文件，确保没有空行
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join([l for l in final_output if l.strip()]))
    
    print(f"同步完成！当前主端口: {main_port}")

if __name__ == "__main__":
    update_live()
