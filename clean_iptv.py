import requests
import re

# 你的原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 绝对保留的分组白名单（严格对应你的截图，包含直播电影台）
KEEP_GROUPS = [
    "4K", "香港 HK", "台湾 TW", "大陆 CN", "海外中文 OC", "马来 MY", "日本 JP", 
    "韩国 KR", "英国 UK", "美国 US", "法国 FR", "加拿大 CA", "澳洲 AU", 
    "泰国 TH", "越南 VN", "菲律宾 PH", "印度 India",
    "Sports", "News", "Documentary", "Music", "Kids", 
    "中文(亚洲服务器)"
]

def clean_task():
    try:
        print("正在进行极速精简：只保留直播分组，剔除臃肿点播...")
        # 设置超时，防止因为原始接口点播太多导致下载失败
        res = requests.get(URL, timeout=60) 
        content = res.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 提取原始分组名
                group_match = re.search(r'group-title="([^"]+)"', line)
                
                if group_match:
                    current_group = group_match.group(1)
                    # 关键逻辑：只要是这22个组里的频道，原封不动保留
                    if current_group in KEEP_GROUPS:
                        new_m3u.append(lines[i])      # 原始描述行
                        if i + 1 < len(lines):
                            new_m3u.append(lines[i+1]) # 原始 URL 行
                        keep_count += 1
                i += 2 
            else:
                i += 1
                
        # 写入新文件
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"--- 优化完成 ---")
        print(f"原始点播分组已被彻底剔除。")
        print(f"保留了 {len(KEEP_GROUPS)} 个直播分组，共 {keep_count} 个频道。")
        print(f"现在文件非常清爽，配置将不再失败。")
        
    except Exception as e:
        print(f"处理失败: {e}")

if __name__ == "__main__":
    clean_task()
