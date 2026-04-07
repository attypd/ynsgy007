import requests
import re

# 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 严格执行截图中的 22 个直播分组名，原汁原味搬运
KEEP_GROUPS = [
    "4K", "香港 HK", "台湾 TW", "大陆 CN", "海外中文 OC", "马来 MY", "日本 JP", 
    "韩国 KR", "英国 UK", "美国 US", "法国 FR", "加拿大 CA", "澳洲 AU", 
    "泰国 TH", "越南 VN", "菲律宾 PH", "印度 India",
    "Sports", "News", "Documentary", "Music", "Kids", 
    "中文(亚洲服务器)"
]

def clean_task():
    try:
        print("开始同步主服务器直播分组...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        
        # 统一处理换行符
        content = res.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                group_match = re.search(r'group-title="([^"]+)"', line)
                if group_match:
                    current_group = group_match.group(1)
                    # 只要分组在截图中，则原汁原味保留里面的所有频道
                    if current_group in KEEP_GROUPS:
                        new_m3u.append(lines[i])
                        if i + 1 < len(lines):
                            new_m3u.append(lines[i+1])
                        keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"成功！已同步保留 {keep_count} 个直播频道。")
        
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    clean_task()
