import requests
import datetime

# 1. 你的核心仓库（第一优先级，原封不动）
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

# 2. 外部杂乱接口
EXTRA_SOURCES = [
    "http://d.jsy777.top/box/tvzb9.txt",                  # 今日影视 (天映/Celestial)
    "https://bc.188766.xyz/?ip=&mima=mianfeibuhuaqian", # 冰茶
    "http://rihou.cc:555/gggg.nzk",
    "http://iptv.4666888.xyz/FYTV.txt"
]
HK_SOURCE = "http://txt.gt.tc/users/HKTV.txt"            # hk快源接口

# 3. 词库设置
WANT_LIST = ["港", "澳", "台", "翡翠", "凤凰", "TVB", "HBO", "星河", "邵氏", "天映", "Celestial", "影院", "电影", "新加坡", "马来西亚", "探索", "地理"]
SECRET_KEYWORDS = ["松视", "成人", "福利", "AV", "18+", "香蕉", "极限", "芭蕉", "午夜"]
BLOCK_KEYWORDS = ["CCTV", "央视", "卫视", "地方", "新闻", "教育", "熊猫", "综艺", "少儿", "纪录", "体育", "电视剧", "歌曲", "购物", "广播"]

OUT_FILE = "bootstrap.min.css"

def get_content(url):
    try:
        # 核心改进：增加模拟浏览器头，防止 hk 等接口拒绝访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(f"{url}?t={datetime.datetime.now().timestamp()}", headers=headers, timeout=25)
        resp.encoding = 'utf-8' # 强制编码，防止乱码
        return resp.text if resp.status_code == 200 else ""
    except Exception as e:
        print(f"❌ 请求失败: {url}, 错误: {e}")
        return ""

def main():
    print("🚀 正在执行终极聚合：正在保护仓库原位、全量抓取hk快源、置底私密分组...")
    content_a, content_b = get_content(SOURCE_A), get_content(SOURCE_B)
    data_b = {l.split(",")[0].strip(): l.split(",")[1].strip() for l in content_b.split('\n') if "," in l and "http" in l}
    
    recorded_ext = set() # 外部接口去重
    final_lines = []
    ext_normal_lines = [] # 外部优选（含港台、天映、hkTV）
    ext_secret_lines = [] # 外部私密（松视、香蕉等）
    
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')

    # --- 第一部分：你的仓库 A+B 内容（原封不动） ---
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
                recorded_ext.add(name.strip()) # 标记已存在，避免外部重复
                if name.strip() in data_b:
                    final_lines.append(f"{name.strip()}(备),{data_b[name.strip()]}")

    # --- 第二部分：专项处理 hk 接口（保证快源全量进入） ---
    hk_content = get_content(HK_SOURCE)
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

    # --- 第三部分：从其他外部接口提取 Celestial、邵氏、冰茶等 ---
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

    # --- 第四部分：拼装输出 ---
    if ext_normal_lines:
        final_lines.append("✨ 外部海外优选(补位),#genre#")
        final_lines.extend(ext_normal_lines)
    
    if ext_secret_lines:
        final_lines.append("私密频道,#genre#")
        final_lines.extend(ext_secret_lines)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
    print(f"✅ 完成！hk快源与Celestial系列已成功整合。")

if __name__ == "__main__":
    main()
