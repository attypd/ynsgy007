import requests
import datetime
import time

# 1. 核心仓库（原位保留，确保你的松视、澳门第一优先级）
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部接口
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",                  # 今日影视 (天映/Celestial)
    "http://rihou.cc:555/gggg.nzk",                      # 555接口 (加严过滤)
    "http://iptv.4666888.xyz/FYTV.txt"
]
HK_SOURCE = "http://txt.gt.tc/users/HKTV.txt"            # hk快源 (针对性强攻)

# 3. 目标关键词
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "新加坡", "马来西亚", "探索", "地理"]
SECRET_KEYWORDS = ["松视", "香蕉", "芭蕉", "极限", "成人", "福利", "AV", "18+", "午夜", "私密"]

# 4. 【超级黑名单】屏蔽内地、地方台、歌曲、体育赛事、点播集数
BLOCK_KEYWORDS = [
    "CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", 
    "体育", "NBA", "赛事", "回放", "全场", "公开赛", "歌曲", "购物", "广播", "内地", 
    "河北", "河南", "山东", "广东台", "集", "点播", "轮播", "系列", "影院", "影迷", 
    "动作", "喜剧", "恐怖", "剧场", "电影院"
]

OUT_FILE = "bootstrap.min.css"

def get_content(url, is_hktv=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # hk 接口响应极慢，给予 60 秒极长等待时间
        timeout_val = 60 if is_hktv else 20
        resp = requests.get(f"{url}?t={int(time.time())}", headers=headers, timeout=timeout_val)
        if resp.status_code == 200:
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        return ""
    except:
        return ""

def main():
    print("🚀 启动强力除杂聚合：屏蔽内地/体育，强攻 hkTV 私密源...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    recorded_ext = set() 
    final_lines = []
    ext_normal_lines = [] # 优选港台
    ext_secret_lines = [] # 私密归类（芭蕉、松视等）
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：仓库源 A+B (原位保留) ---
    if content_a:
        for line in content_a.split('\n'):
            line = line.strip()
            if not line: continue
            if "#genre#" in line:
                final_lines.append(f"🛡️ 聚合热备 {bj_time},#genre#" if not final_lines else line)
                continue
            if "," in line and "http" in line:
                name, url = line.split(",", 1)
                name = name.strip()
                final_lines.append(f"{name},{url.strip()}")
                recorded_ext.add(name)
                if name in data_b:
                    final_lines.append(f"{name}(备),{data_b[name]}")

    # --- 第二部分：强攻 hk 接口 (只要不含黑名单，全量提取补位) ---
    hk_content = get_content(HK_SOURCE, is_hktv=True)
    if hk_content:
        for line in hk_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                # 过滤体育赛事和内地杂质
                if any(b in name for b in BLOCK_KEYWORDS): continue
                if name in recorded_ext: continue
                
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                else:
                    ext_normal_lines.append(line)
                recorded_ext.add(name)

    # --- 第三部分：其他接口提取 (今日影视/555) ---
    for url in EXTRA_SOURCES:
        ext_content = get_content(url)
        for line in ext_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                if any(b in name for b in BLOCK_KEYWORDS) or name in recorded_ext: continue
                
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                    recorded_ext.add(name)
                elif any(w in name for w in WANT_LIST):
                    ext_normal_lines.append(line)
                    recorded_ext.add(name)

    # --- 第四部分：组装 ---
    if ext_normal_lines:
        final_lines.append("✨ 外部海外补位(含天映/hkTV),#genre#")
        final_lines.extend(ext_normal_lines)
    
    if ext_secret_lines:
        # 你要求的最后一个分组：含芭蕉、松视等
        final_lines.append("私密频道,#genre#")
        final_lines.extend(ext_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 任务完成！已剔除体育/内地杂质，并强化提取 hkTV。")

if __name__ == "__main__":
    main()
