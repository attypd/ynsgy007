import requests
import datetime

# 你的两个 Raw 链接
SOURCE_A = "https://raw.githubusercontent.com/attypd/shyio002/refs/heads/main/total_live.txt"
SOURCE_B = "https://raw.githubusercontent.com/attypd/ynsgu003/refs/heads/main/total_live.txt"

OUT_FILE = "bootstrap.min.css"

def get_content(url):
    try:
        resp = requests.get(f"{url}?t={datetime.datetime.now().timestamp()}", timeout=15)
        return resp.text if resp.status_code == 200 else ""
    except:
        return ""

def main():
    print(f"📡 正在深度聚合（保留分组）...")
    content_a = get_content(SOURCE_A)
    content_b = get_content(SOURCE_B)
    
    if not content_a and not content_b:
        print("❌ 未抓取到任何数据")
        return

    # 先把源 B 解析成字典，方便快速查询备用线
    data_b = {}
    for line in content_b.split('\n'):
        if "," in line and "http" in line:
            parts = line.split(",", 1)
            data_b[parts[0].strip()] = parts[1].strip()

    # 处理源 A 并生成最终文件
    final_lines = []
    bj_time = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%m-%d %H:%M')
    
    # 记录已经处理过的频道，防止重复
    processed_in_a = set()

    lines_a = content_a.split('\n')
    for line in lines_a:
        line = line.strip()
        if not line: continue
        
        # 1. 保留分组行
        if "#genre#" in line:
            # 如果是第一行，加上我们的聚合时间戳
            if not final_lines:
                final_lines.append(f"🛡️ 聚合热备 {bj_time},#genre#")
            else:
                final_lines.append(line)
            continue

        # 2. 处理频道行
        if "," in line and "http" in line:
            parts = line.split(",", 1)
            name = parts[0].strip()
            url_a = parts[1].strip()
            
            # 写入主线（来自源A）
            final_lines.append(f"{name},{url_a}")
            processed_in_a.add(name)
            
            # 查找源 B 是否有同名频道，如果有且链接不同，作为备用线
            url_b = data_b.get(name)
            if url_b and url_b != url_a:
                final_lines.append(f"{name}(备),{url_b}")

    # 3. 补漏：如果源 B 有 A 里完全没有的频道，放在最后的一个新分类里
    new_channels_from_b = [n for n in data_b if n not in processed_in_a]
    if new_channels_from_b:
        final_lines.append("✨ 其他新增资源,#genre#")
        for name in new_channels_from_b:
            final_lines.append(f"{name},{data_b[name]}")

    # 写入结果
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(final_lines))
                
    print(f"✅ 聚合完成！已保留分组并添加热备线路。")

if __name__ == "__main__":
    main()
