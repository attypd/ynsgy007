import requests
import re
import socket
import os
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store" # Main Server
PRIVATE_FILE = "my20262.6.txt"

# Scanning Priority: 4-5w -> 3-4w -> 5-6.5w -> 1-3w
PORT_RANGES = [
    range(40000, 50001), 
    range(30000, 40000), 
    range(50001, 65536), 
    range(10000, 30000)
]

TIMEOUT = 0.4 
MAX_WORKERS = 1000 

def check_port_alive(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return str(port) if s.connect_ex((TARGET_HOST, int(port))) == 0 else None
    except: return None

def fix_only_main_host(line, new_port):
    """Replace port ONLY for url.cdnhs.store"""
    if TARGET_HOST in line:
        return re.sub(rf'({re.escape(TARGET_HOST)}):(\d+)', rf'\1:{new_port}', line)
    return line

def update_live():
    # --- STEP 1: SCAN PORTS ---
    print(f"Scanning {TARGET_HOST}...")
    main_port = None
    for p_range in PORT_RANGES:
        if main_port: break
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(check_port_alive, p_range)
            for r in results:
                if r:
                    main_port = r
                    print(f"Port Found: {main_port} ({p_range.start}-{p_range.stop})")
                    break
    
    if not main_port: main_port = "40700" 

    # --- STEP 2: FETCH PHP ---
    php_content = ""
    php_is_valid = False
    try:
        resp = requests.get(PHP_URL, timeout=5)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_content = resp.text
            # Verify if PHP content is still active
            p_found = re.findall(rf'{re.escape(TARGET_HOST)}:(\d+)', php_content)
            if p_found and check_port_alive(p_found[0]):
                php_is_valid = True
    except: 
        print("PHP invalid, using scan rescue mode.")

    final_output = []
    has_private_group = False

    # --- STEP 3: PROCESS DATA ---
    if php_content:
        lines = php_content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            if "分类名称" in line:
                g_name = line.replace("分类名称：", "").replace("分类名称:", "").strip()
                is_private = "私密" in g_name
                if is_private:
                    has_private_group = True
                    if "_1818" not in g_name: g_name += "_1818" # Password 1818
                
                # Genre Format: Name,#genre#
                final_output.append(f"\n{g_name},#genre#")
                
                if is_private:
                    temp_ch = []
                    for j in range(i + 1, len(lines)):
                        nxt = lines[j].strip()
                        if "分类名称" in nxt: break
                        if "," in nxt: temp_ch.append(nxt)
                    
                    for c in temp_ch:
                        if not php_is_valid:
                            c = fix_only_main_host(c, main_port)
                        final_output.append(c)
                    
                    # Mirror Backup Group
                    if temp_ch:
                        # Keep Chinese (备) for better UI display
                        b_title = g_name.replace("_1818", "") + "(备)_1818"
                        final_output.append(f"\n{b_title},#genre#")
                        for c in temp_ch:
                            final_output.append(fix_only_main_host(c, main_port))
            
            elif "," in line and "http" in line:
                is_done = False
                for k in range(len(final_output)-1, -1, -1):
                    if "#genre#" in final_output[k]:
                        if "私密" in final_output[k]: is_done = True
                        break
                if not is_done:
                    if not php_is_valid:
                        line = fix_only_main_host(line, main_port)
                    final_output.append(line)

    # --- STEP 4: REPOSITORY BACKUP ---
    if (not php_content or not has_private_group) and os.path.exists(PRIVATE_FILE):
        final_output.append("\n私密频道_1818,#genre#")
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            for pl in f:
                pl = pl.strip()
                if "," in pl:
                    pl = fix_only_main_host(pl, main_port)
                    final_output.append(pl)

    # --- STEP 5: SAVE ---
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join([l for l in final_output if l.strip()]))
    
    print(f"Task Done. Active Port: {main_port}")

if __name__ == "__main__":
    update_live()
