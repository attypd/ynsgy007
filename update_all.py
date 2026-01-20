import requests
import datetime
import time

# 1. 核心仓库（原位保留，你的松视、澳门在最前面）
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部接口（调整顺序：今日影视排在第一位，确保天映和邵氏优先）
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",                  # 今日影视 (天映/邵氏重镇)
    "http://rihou.cc:555/gggg.nzk",                      # 555接口
    "http://iptv.4666888.xyz/FYTV.txt"
]
HK_SOURCE = "http://txt.gt.tc/users/HKTV.txt"            # hk快源 (目标：松视、芭蕉)

# 3. 目标优选词库（加入邵氏）
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "新加坡", "马来西亚", "探索", "地理"]

# 4. 私密关键词
SECRET_KEYWORDS = ["松视", "香蕉", "芭蕉", "极限", "成人", "福利", "AV", "18+", "午夜", "私密", "Jav"]

# 5. 【严厉黑名单】屏蔽内地、地方台、歌曲、体育赛事、集数点播
BLOCK_KEYWORDS = [
    "CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", "体育", 
    "NBA", "赛事", "回放", "全场", "VS", "公开赛", "图文", "桌", "WTT", "乒乓球", "足球",
    "歌曲", "音乐", "精选", "首", "专辑", "MV", "演唱会", "购物", "广播", "内地", "集", "点播", "轮播"
]

OUT_FILE = "bootstrap.min.css"

def get_content(url, is_hktv=False):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # 给 hkTV 接口留足 60 秒强攻时间
        timeout_val = 60 if is_hktv else 25
        resp = requests.get(f"{url}?t={int(time.time())}", headers=headers, timeout=timeout_val)
        if resp.status_code == 200:
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        return ""
    except: return ""

def main():
    print("🚀 启动深度聚合：优先今日影视(天映/邵氏)，强攻 hkTV(松视/芭蕉)...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    recorded_ext = set() 
    final_lines = []
    ext_normal_lines = [] # 优选补位
    ext_secret_lines = [] # 私密归类
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：仓库源 (原封不动) ---
    if content_a:
        for line in content_a.split('\n'):
            line = line.strip()
            if not line or "#genre#" in line:
                if "#genre#" in line: final_lines.append(f"🛡️ 聚合热备 {bj_time},#genre#" if not final_lines else line)
                continue
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                final_lines.append(line)
                recorded_ext.add(name)
                if name in data_b: final_lines.append(f"{name}(备),{data_b[name]}")

    # --- 第二部分：处理 hkTV 接口 (优先提取私密和快源) ---
    hk_content = get_content(HK_SOURCE, is_hktv=True)
    if hk_content:
        for line in hk_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                if any(b in name for b in BLOCK_KEYWORDS): continue
                if name in recorded_ext: continue
                
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                else:
                    ext_normal_lines.append(line)
                recorded_ext.add(name)

    # --- 第三部分：处理其他接口 (今日影视排在最前) ---
    for url in EXTRA_SOURCES:
        ext_content = get_content(url)
        for line in ext_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                # 过滤杂质，但如果名字里带“邵氏”或“天映”则放行
                if any(b in name for b in BLOCK_KEYWORDS):
                    if not any(w in name for w in ["邵氏", "天映", "Celestial"]):
                        continue
                
                if name in recorded_ext: continue
                
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                    recorded_ext.add(name)
                elif any(w in name for w in WANT_LIST):
                    ext_normal_lines.append(line)
                    recorded_ext.add(name)

    # --- 第四部分：组装 ---
    if ext_normal_lines:
        final_lines.append("✨ 外部海外补位(天映/邵氏/hkTV),#genre#")
        final_lines.extend(ext_normal_lines)
    
    if ext_secret_lines:
        final_lines.append("私密频道,#genre#")
        final_lines.extend(ext_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 完成！天映、邵氏、hk港台及私密源已全部就位，垃圾频道已剔除。")

if __name__ == "__main__":
    main()
