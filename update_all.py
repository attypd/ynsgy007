import requests
import datetime

# 1. 你的两个“双路热备”链接
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部杂乱接口列表
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",
    "http://rihou.cc:555/gggg.nzk",
    "https://bc.188766.xyz/?ip=&mima=mianfeibuhuaqian",
    "http://iptv.4666888.xyz/FYTV.txt",
    "http://txt.gt.tc/users/HKTV.txt"
]

# 3. 【优选点菜名单】
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "新加坡", "马来西亚", "探索", "地理"]

# 4. 【外部私密名单】
SECRET_KEYWORDS = ["松视", "成人", "福利", "AV", "18+"]

# 5. 【绝对黑名单】（外部接口里的杂质）
BLOCK_KEYWORDS = ["CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", "体育", "电视剧", "歌曲", "购物", "广播"]

OUT_FILE = "bootstrap.min.css"

def get_content(url):
    try:
        resp = requests.get(f"{url}?t={datetime.datetime.now().timestamp()}", timeout=15)
        return resp.text if resp.status_code == 200 else ""
    except: return ""

def main():
    print("🚀 正在执行聚合：外部港台内部去重，确保补位源纯净...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    # 用来记录外部接口已经提取过的频道，防止外部源之间相互重复
    external_recorded = set()
    final_lines = []
    external_normal_lines = [] 
    external_secret_lines = [] 
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：完整保留你仓库 A+B 的内容 ---
    if content_a:
        for line in content_a.split('\n'):
            line = line.strip()
            if not line: continue
            if "#genre#" in line:
                final_lines.append(f"🛡️ 聚合热备 {bj_time},#genre#" if not final_lines else line)
                continue
            if "," in line and "http" in line:
                name, url_a = line.split(",", 1)
                name = name.strip()
                final_lines.append(f"{name},{url_a.strip()}")
                if name in data_b: final_lines.append(f"{name}(备),{data_b[name]}")

    # --- 第二部分：从外部接口提取补充（外部源之间进行去重） ---
    for url in EXTRA_SOURCES:
        ext = get_content(url)
        if not ext: continue
        for line in ext.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                
                # 1. 过滤掉绝对不要的杂质
                if any(b in name for b in BLOCK_KEYWORDS): continue
                # 2. 如果外部接口已经提取过这个名字了，就跳过（实现外部去重）
                if name in external_recorded: continue

                # A. 提取外部私密频道
                if any(s in name for s in SECRET_KEYWORDS):
                    external_secret_lines.append(line)
                    external_recorded.add(name)
                
                # B. 提取优选港台（补位源）
                elif any(w in name for w in WANT_LIST):
                    external_normal_lines.append(line)
                    external_recorded.add(name)

    # --- 第三部分：拼装 ---
    if external_normal_lines:
        final_lines.append("✨ 外部海外优选(补位),#genre#")
        final_lines.extend(external_normal_lines)
    
    if external_secret_lines:
        final_lines.append("私密频道,#genre#")
        final_lines.extend(external_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 聚合完成！外部重复港台已过滤，杂质已清除。")

if __name__ == "__main__":
    main()
