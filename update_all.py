import requests
import datetime
import time

# 1. 你的核心仓库（绝对原位保留，不挪动）
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部接口（去掉了冰茶，保留今日影视、555、FYTV）
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",                  # 今日影视 (天映/Celestial)
    "http://rihou.cc:555/gggg.nzk",                      # 555接口
    "http://iptv.4666888.xyz/FYTV.txt"
]
HK_SOURCE = "http://txt.gt.tc/users/HKTV.txt"            # hk快源接口

# 3. 词库设置
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "新加坡", "马来西亚", "探索", "地理"]

# 重点：包含你提到的“芭蕉”等所有私密关键词
SECRET_KEYWORDS = ["松视", "香蕉", "芭蕉", "极限", "成人", "福利", "AV", "18+", "午夜", "私密"]

# 严厉打击 555 等接口里的电视剧、轮播等杂质
BLOCK_KEYWORDS = [
    "CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", "体育", 
    "电视剧", "点播", "轮播", "系列", "影院", "影迷", "动作", "喜剧", "恐怖", "歌曲", 
    "购物", "广播", "内地", "少儿", "纪录", "河北", "河南", "山东", "广东台"
]

OUT_FILE = "bootstrap.min.css"

def get_content(url, is_hktv=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # 给 hk 接口留足 45 秒，防止响应慢
        timeout_val = 45 if is_hktv else 20
        resp = requests.get(f"{url}?t={int(time.time())}", headers=headers, timeout=timeout_val)
        if resp.status_code == 200:
            resp.encoding = resp.apparent_encoding or 'utf-8'
            return resp.text
        return ""
    except:
        return ""

def main():
    print("🚀 启动定制聚合：正在提取 hk 接口中的港台与“芭蕉”源...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    recorded_ext = set() 
    final_lines = []
    ext_normal_lines = [] # 外部优选补位
    ext_secret_lines = [] # 外部私密（芭蕉、松视等）
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：仓库源 A+B (原汁原味，位置不动) ---
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
                recorded_ext.add(name) # 仓库已有的，外部不再重复
                if name in data_b:
                    final_lines.append(f"{name}(备),{data_b[name]}")

    # --- 第二部分：强攻 hk 接口 (只要是港台快源和芭蕉，全要) ---
    hk_content = get_content(HK_SOURCE, is_hktv=True)
    if hk_content:
        for line in hk_content.split('\n'):
            line = line.strip()
            if "," in line and "http" in line:
                name = line.split(",")[0].strip()
                if any(b in name for b in BLOCK_KEYWORDS): continue
                if name in recorded_ext: continue
                
                # 识别并分类芭蕉/松视等
                if any(s in name for s in SECRET_KEYWORDS):
                    ext_secret_lines.append(line)
                else:
                    ext_normal_lines.append(line)
                recorded_ext.add(name)

    # --- 第三部分：其他接口提取 (今日影视 Celestial/港台) ---
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

    # --- 第四部分：拼装 ---
    if ext_normal_lines:
        final_lines.append("✨ 外部海外补位(含天映/hkTV),#genre#")
        final_lines.extend(ext_normal_lines)
    
    if ext_secret_lines:
        # 这里就是你要求的最后一个分组，管它叫芭蕉还是什么，全在这里
        final_lines.append("私密频道,#genre#")
        final_lines.extend(ext_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 聚合完成！“芭蕉”等源已归类置底。")

if __name__ == "__main__":
    main()
