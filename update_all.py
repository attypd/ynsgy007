import requests, re, socket, os
from concurrent.futures import ThreadPoolExecutor

# --- CONFIG ---
PHP_URL = "http://atryffad.usa3.345123.xyz/ww.php?id=2"
TARGET_HOST = "url.cdnhs.store" 
PRIVATE_FILE = "my20262.6.txt"

# Priority Port Ranges: 4-5w -> 3-4w -> 5-6.5w -> 1-3w
PORT_RANGES = [range(40000, 50001), range(30000, 40000), range(50001, 65536), range(10000, 30000)]
TIMEOUT, MAX_WORKERS = 0.4, 1000 

def check_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            return str(port) if s.connect_ex((TARGET_HOST, int(port))) == 0 else None
    except: return None

def fix_port(line, p):
    """Only replace port for the main host"""
    if TARGET_HOST in line:
        return re.sub(rf'({re.escape(TARGET_HOST)}):(\d+)', rf'\1:{p}', line)
    return line

def update_live():
    print(f"Scanning {TARGET_HOST}...")
    main_p = None
    for pr in PORT_RANGES:
        if main_p: break
        with ThreadPoolExecutor(MAX_WORKERS) as ex:
            res = ex.map(check_port, pr)
            for r in res:
                if r: main_p = r; print(f"Active Port: {r}"); break
    if not main_p: main_p = "40700"

    php_c, php_v = "", False
    try:
        resp = requests.get(PHP_URL, timeout=5)
        resp.encoding = 'utf-8'
        if resp.status_code == 200:
            php_c = resp.text
            pf = re.findall(rf'{re.escape(TARGET_HOST)}:(\d+)', php_c)
            if pf and check_port(pf[0]): php_v = True
    except: print("PHP link invalid.")

    out, has_p = [], False
    if php_c:
        lines = php_c.split('\n')
        for i, l in enumerate(lines):
            l = l.strip()
            if not l: continue
            if "分类名称" in l:
                gn = l.replace("分类名称：", "").replace("分类名称:", "").strip()
                is_p = "私密" in gn
                if is_p:
                    has_p = True
                    if "_1818" not in gn: gn += "_1818"
                out.append(f"\n{gn},#genre#") # Standard format
                if is_p:
                    tmp = []
                    for j in range(i + 1, len(lines)):
                        nxt = lines[j].strip()
                        if "分类名称" in nxt: break
                        if "," in nxt: tmp.append(nxt)
                    for c in tmp: out.append(fix_port(c, main_p) if not php_v else c)
                    if tmp:
                        out.append(f"\n{gn.replace('_1818', '')}(备)_1818,#genre#")
                        for c in tmp: out.append(fix_port(c, main_p))
            elif "," in l and "http" in l:
                done = False
                for k in range(len(out)-1, -1, -1):
                    if "#genre#" in out[k] and "私密" in out[k]: done = True; break
                if not done: out.append(fix_port(l, main_p) if not php_v else l)

    # Repository backup if PHP fails
    if (not php_c or not has_p) and os.path.exists(PRIVATE_FILE):
        out.append("\n私密频道_1818,#genre#")
        with open(PRIVATE_FILE, 'r', encoding='utf-8') as f:
            for pl in f:
                pl = pl.strip()
                if "," in pl: out.append(fix_port(pl, main_p))

    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join([ln for ln in out if ln.strip()]))
    print("Update Completed.")

if __name__ == "__main__":
    update_live()
