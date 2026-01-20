import requests
import datetime

# 填入你提供的两个 Raw 结果链接
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

OUT_FILE = "bootstrap.min.css"

def get_content(url):
    try:
        # 加上时间戳参数，强制获取 GitHub 最新的数据，不走缓存
        resp = requests.get(f"{url}?t={datetime.datetime.now().timestamp()}", timeout=15)
        return resp.text if resp.status_code == 200 else ""
    except:
        return ""

def main():
    print(f"📡 正在聚合数据...")
    content_a = get_content(SOURCE_A)
    content_b = get_content(SOURCE_B)
    
    # 提取线路（兼容：频道名,链接 格式）
    def parse_to_dict(content):
        res = {}
        if not content: return res
        for line in content.split('\n'):
            if "," in line and "http" in line:
                parts = line.split(",", 1)
                res[parts[0].strip()] = parts[1].strip()
        return res

    data_a = parse_to_dict(content_a)
    data_b = parse_to_dict(content_b)

    # 合并逻辑：将 A 和 B 的频道汇总
    all_names = set(list(data_a.keys()) + list(data_b.keys()))
    
    if not all_names:
        print("⚠️ 未抓取到有效内容，请检查上游链接。")
        return

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        # 获取北京时间
        bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')
        f.write(f"🛡️ 聚合双路热备 {bj_time} (A:{len(data_a)} B:{len(data_b)}),#genre#\n")
        
        # 按照频道名称排序
        for name in sorted(all_names):
            url_a = data_a.get(name)
            url_b = data_b.get(name)
            
            # 第一行作为主线
            if url_a:
                f.write(f"{name},{url_a}\n")
            
            # 如果 B 有不同的链接，作为(备)线存入，解决黑屏切换麻烦
            if url_b and url_b != url_a:
                f.write(f"{name}(备),{url_b}\n")
                
    print(f"✅ 聚合成功！文件已保存至 {OUT_FILE}")

if __name__ == "__main__":
    main()
