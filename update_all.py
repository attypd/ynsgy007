import requests
import re
import socket
import os
from concurrent.futures import ThreadPoolExecutor

# 配置信息
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store"
PRIVATE_FILE = "my20262.6.txt"  # 仓库中的私密源文件
# 端口扫描范围：8080 以及常用的 40000-50000
SCAN_PORTS = [8080] + list(range(40000, 50001))
TIMEOUT = 1.0

def check_port_alive(port):
    """检测端口是否存活 (只要能建立连接即视为有效)"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            if s.connect_ex((TARGET_HOST, port)) == 0:
                return str(port)
    except:
        pass
    return None

def scan_for_ports():
    """多线程扫描 4w-5w 端口以获取最新有效端口"""
    print(f"正在扫描 {TARGET_HOST} 的有效端口...")
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_port_alive, SCAN_PORTS)
    return [p for p in results if p]

def get_private_content(ports):
    """读取并修正私密频道文件中的端口"""
    if not os.path.exists(PRIVATE_FILE):
        return ""
    
    with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取最新的两个端口实现双线支持
    main_port = ports[0]
    # 将文件内所有旧端口替换为当前扫描到的最新有效端口
    content = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", content)
    return content

def update_live():
    valid_ports = []
    php_content = ""
    
    # 1. 优先从 PHP 接口获取并验证端口
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(PHP_URL, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
            found = re.findall(r'url\.cdnhs\.store:(\d+)', php_content)
            for p in set(found):
                if check_port_alive(int(p)): 
                    valid_ports.append(p)
    except:
        print("PHP 接口不可用。")

    # 2. 如果 PHP 无效或没提供端口，启动 4w-5w 扫描备份
    if not valid_ports:
        valid_ports = scan_for_ports()

    if not valid_ports:
        print("未发现有效端口，跳过更新。")
        return

    main_port = valid_ports[0]
    print(f"当前探测到的最新有效端口: {main_port}")

    # 3. 处理 PHP 返回的数据并强制规范化分组
    new_lines = []
    has_private_in_php = False
    
    if php_content:
        for line in php_content.split('\n'):
            line = line.strip()
            if not line: continue
            
            # 格式转换：从“分类名称：”转为标准“名称#genre#”
            if "分类名称：" in line:
                genre = line.replace("分类名称：", "").strip()
                if "私密" in genre: 
                    has_private_in_php = True
                    # 强制为私密分组加上密码 1818
                    new_lines.append(f"\n{genre}_1818#genre#")
                else:
                    new_lines.append(f"\n{genre}#genre#")
            
            elif "," in line and "http" in line:
                # 同步修正 PHP 内容里的端口
                line = re.sub(r'url\.cdnhs\.store:\d+', f"{TARGET_HOST}:{main_port}", line)
                new_lines.append(line)

    # 4. 自动补全：若 PHP 无私密分组，则从 my20262.6.txt 补全
    if not has_private_in_php:
        print("检测到私密分组缺失，正在从本地仓库补全...")
        private_data = get_private_content(valid_ports)
        if private_data:
            # 确保分组名带有标准格式和密码
            if "#genre#" not in private_data:
                new_lines.append("\n私密频道_1818#genre#")
            new_lines.append(private_data.strip())

    # 5. 生成标准 TXT 文件
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines).strip())
    print(f"更新成功！total_live.txt 已同步最新端口: {main_port}")

if __name__ == "__main__":
    update_live()
