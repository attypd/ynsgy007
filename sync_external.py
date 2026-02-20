import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- 核心配置 ---
DOMAIN = "url.cdnhs.store"
EXTERNAL_API = "https://feer-cdn-bp.xpnb.qzz.io/xnkl.txt"
SOURCE_FILE = "cvs_mylive.txt"  # 用于提取私密频道分组
OUTPUT_FILE = "gar_extra.txt"

def check_port(port):
    """三段式极速扫描探测"""
    test_url = f"http://{DOMAIN}:{port}/mytv.php?id=3"
    try:
        res = requests.head(test_url, timeout=1.5, allow_redirects=False)
        if res.status_code in [200, 302]: return str(port)
    except: return None
    return None

def run_scanner(port_list):
    """高并发探测"""
    random.shuffle(port_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """三段式全端口保底"""
    res = run_scanner(list(range(40000, 50001))) or \
          run_scanner(list(range(30000, 40000)) + list(range(50001, 65536))) or \
          run_scanner(list(range(8000, 30000)))
    return res if res else "48559"

def sync_gar_with_regions():
    active_port = get_latest_port()
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    # 按照你的需求定义地区分组
    groups = {
        "香港频道": [],
        "台湾频道": [],
        "内地频道": [],
        "国际频道": [],
        "精选频道": []
    }
    
    # 1. 抓取外部接口并执行地区识别
    try:
        resp = requests.get(EXTERNAL_API, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            for line in resp.text.split('\n'):
                line = line.strip()
                if "," in line and "#genre#" not in line:
                    name = line.split(',')[0].upper()
                    # 端口同步
                    if DOMAIN in line:
                        line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line)
                    
                    # --- 地区识别逻辑 ---
                    if any(x in name for x in ["香港", "HK", "TVB", "翡翠"]): 
                        groups["香港频道"].append(line)
                    elif any(x in name for x in ["台湾", "TW", "中天", "年代", "东森"]): 
                        groups["台湾频道"].append(line)
                    elif any(x in name for x in ["CCTV", "卫视", "内地"]): 
                        groups["内地频道"].append(line)
                    elif any(x in name for x in ["HBO", "CNN", "BBC", "DISCOVERY", "国际"]): 
                        groups["国际频道"].append(line)
                    else:
                        groups["精选频道"].append(line)
    except: 
        print("External API offline")

    # 2. 构造最终内容
    final_output = []
    for g_name, g_list in groups.items():
        if g_list:
            final_output.append(f"{g_name},#genre#")
            final_output.extend(g_list)
            final_output.append("") # 分组间空行

    # 3. 提取本地私密频道分组并置底
    private_group = []
    is_private = False
    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "私密频道" in line: is_private = True
                if is_private:
                    if DOMAIN in line:
                        line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line)
                    private_group.append(line)
    except: pass

    if private_group:
        final_output.extend(private_group)

    # 4. 写入独立文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_output))
        f.write(f"\n\n# Region-Sync: {sync_time} | Port: {active_port}")
    
    print(f"File {OUTPUT_FILE} created successfully.")

if __name__ == "__main__":
    sync_gar_with_regions()
