import requests
import re
import socket
import os
from concurrent.futures import ThreadPoolExecutor

# 配置信息
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store"
PRIVATE_FILE = "my20262.6.txt"
SCAN_PORTS = [8080, 40700, 41761, 48370] + list(range(40000, 50001))
TIMEOUT = 0.8

def check_port_alive(port):
    """探测端口是否连通"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return str(port) if s.connect_ex((TARGET_HOST, int(port))) == 0 else None
    except: return None

def update_live():
    # 1. 【先行自救扫描】获取当前主服务器最新、最快的端口
    print("正在扫描主服务器实时端口以备救援...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        scan_results = executor.map(check_port_alive, SCAN_PORTS)
    valid_scan = [r for r in scan_results if r]
    main_port = valid_scan[0] if valid_scan else "40700" # 扫描保底

    # 2. 获取 PHP 原始数据
    php_content = ""
    php_is_working = False
    try:
        resp = requests.get(PHP_URL, timeout=8)
        resp.encoding = 'utf-8'
        if resp.status_code == 200 and "url.cdnhs.store" in resp.text:
            php_content = resp.text
            # 检查 PHP 当前用的端口是否还能通
            php_ports = re.findall(r'url\.cdnhs\.store:(\d+)', php_content)
            if php_ports and check_port_alive(php_ports[0]):
                php_is_working = True
    except: pass

    final_output = []
    has_private_in_php = False

    # 3. 处理 PHP 内容 (优先利用)
    if php_content:
        lines = php_content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # 分组行处理：强制标准格式 名称,#genre#
            if "分类名称" in line:
                g_name = line.replace("分类名称：", "").replace("分类名称:", "").strip()
                is_private = "私密" in g_name
                if is_private:
                    has_private_in_php = True
                    g_name = g_name + "_1818" if "_1818" not in g_name else g_name
                
                final_output.append(f"\n{g_name},#genre#")
                
                # 如果是私密组，立刻提取其频道并生成【私密分组备】
                if is_private:
                    temp_channels = []
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if "分类名称" in next_line: break
                        if "," in next_line: temp_channels.append(next_line)
                    
                    # 放入 PHP 原始频道 (如果 PHP 坏了，这里也自动换成新扫描的端口)
                    for c in temp_channels:
                        if not php_is_working:
                            c = re.sub(r':\d+', f":{main_port}", c)
                        final_output.append(c)
                    
                    # 【核心目的】：额外多加一个私密分组备，强制跟随主服务器最新端口
                    if temp_channels:
                        backup_title = g_name.replace("_1818", "") + "(备)_1818"
                        final_output.append(f"\n{backup_title},#genre#")
                        for c in temp_channels:
                            # 备用组强制使用扫描到的 main_port
                            c_backup = re.sub(r':\d+', f":{main_port}", c)
                            final_output.append(c_backup)
            
            # 普通频道行（非私密组）
            elif "," in line and "http" in line:
                # 如果 PHP 坏了，强制全套源跟随最新扫描端口
                if not php_is_working:
                    line = re.sub(r':\d+', f":{main_port}", line)
                
                # 避免重复添加（私密组逻辑已处理完其名下频道）
                is_processed = False
                for k in range(len(final_output)-1, -1, -1):
                    if "#genre#" in final_output[k]:
                        if "私密" in final_output[k]: is_processed = True
                        break
                if not is_processed: final_output.append(line)

    # 4. 【补全逻辑】当 PHP 坏了、没内容、或 PHP 里没有私密分组时，添加仓库备用
    if (not php_content or not has_private_in_php) and os.path.exists(PRIVATE_FILE):
        print("触发仓库保底机制...")
        final_output.append("\n私密频道_1818,#genre#")
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            for p_line in f:
                p_line = p_line.strip()
                if "," in p_line:
                    # 仓库源强制跟随主服务器最新端口
                    p_line = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", p_line)
                    final_output.append(p_line)

    # 5. 写入文件 (确保 100% 生成)
    if final_output:
        with open("total_live.txt", "w", encoding="utf-8") as f:
            f.write("\n".join([l for l in final_output if l.strip()]))
        print(f"脚本执行成功！当前最优端口: {main_port}")
    else:
        print("错误：未获取到任何数据。")

if __name__ == "__main__":
    update_live()
