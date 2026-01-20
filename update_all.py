import requests
import datetime

# 1. 你的核心仓库（第一优先级，原样保留）
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部杂乱接口（按优先级排序）
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",                  # 今日影视 (天映/Celestial重灾区)
    "https://bc.188766.xyz/?ip=&mima=mianfeibuhuaqian", # 冰茶 (港台优选)
    "http://rihou.cc:555/gggg.nzk",
    "http://iptv.4666888.xyz/FYTV.txt"
]
HK_SOURCE = "http://txt.gt.tc/users/HKTV.txt"            # hkTV (快源/私密源)

# 3. 筛选词库
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "影院", "电影", "新加坡", "马来西亚", "探索", "地理"]
SECRET_KEYWORDS = ["松视", "成人", "福利", "AV", "18+", "香蕉", "极限", "芭蕉"]
BLOCK_KEYWORDS = ["CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", "体育", "电视剧", "歌曲", "购物", "广播"]

OUT_FILE = "bootstrap.min.css"

def get_content(url):
    try:
        resp = requests.get(f"{url}?t={datetime.datetime.now().timestamp()}", timeout=15)
        return resp.text if resp.status_code == 200 else ""
    except: return ""

def main():
    print("🚀 开始终极聚合：正在保护仓库原位、提取Celestial、置底hkTV私密源...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    recorded_ext = set() # 外部接口去重
    final_lines = []
    ext_normal_lines = [] 
    ext_secret_lines = [] 
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：你的仓库 A+B 内容（原位置原封不动） ---
    if content_a:
        for line in content_a.split('\n'):
            line = line.strip()
            if not line: continue
            if "#genre#" in line:
                final_lines.append(f"🛡️ 聚合热备 {bj_time},#genre#" if not final_lines else line)
                continue
            if "," in line and "http" in line:
                name, url = line.split(",", 1)
                final_lines.append(f"{name.strip()},{url.strip()}")
                if name.strip() in data_b:
                    final_lines.append(f"{name.strip()}(备),{data_b[name.strip()]}")

    # --- 第二部分：从普通外部接口（今日影视/冰茶等）提取天映、邵氏、港台 ---
    for url in EXTRA_SOURCES:
        ext_content = get_content(url)
        for line in ext_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                if any(b in name for b in BLOCK_KEYWORDS): continue # 剔除垃圾
                if name in recorded_ext: continue # 外部去重
                
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                    recorded_ext.add(name)
                elif any(w in name for w in WANT_LIST):
                    ext_normal_lines.append(line)
                    recorded_ext.add(name)

    # --- 第三部分：全量处理 hkTV 接口（快源 + 私密源） ---
    hktv_content = get_content(HK_SOURCE)
    for line in hktv_content.split('\n'):
        line = line.strip()
        if "," in line and "http" in line:
            name = line.split(",")[0].strip()
            if name in recorded_ext: continue
            
            # hkTV 的私密频道直接进私密组
            if any(s in name for s in SECRET_KEYWORDS):
                ext_secret_lines.append(line)
                recorded_ext.add(name)
            # hkTV 的港台源（全留，只要不属于垃圾名单）
            elif not any(b in name for b in BLOCK_KEYWORDS):
                ext_normal_lines.append(line)
                recorded_ext.add(name)

    # --- 第四部分：按照你要求的顺序组装 ---
    if ext_normal_lines:
        final_lines.append("✨ 外部海外补位(含天映/hkTV),#genre#")
        final_lines.extend(ext_normal_lines)
    
    if ext_secret_lines:
        final_lines.append("私密频道,#genre#")
        final_lines.extend(ext_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 完成！仓库源在顶，天映补位在中，hkTV港台全留，私密已置底。")

if __name__ == "__main__":
    main()
