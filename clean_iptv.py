import requests
import re

# 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 严格锁定你 8 张截图里的 22 个直播分组名，一个都不能漏
# 只有这些组里的频道会被“原汁原味”保留，其他的电影点播全部剔除
KEEP_GROUPS = [
    "4K", "香港 HK", "台湾 TW", "大陆 CN", "海外中文 OC", "马来 MY", "日本 JP", 
    "韩国 KR", "英国 UK", "美国 US", "法国 FR", "加拿大 CA", "澳洲 AU", 
    "泰国 TH", "越南 VN", "菲律宾 PH", "印度 India",
    "Sports", "News", "Documentary", "Music", "Kids", 
    "中文(亚洲服务器)"
]

def clean_task():
    try:
        print("开始原味提取直播分组，剔除点播库...")
        # 增加超时时间确保大文件下载
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
                # 动态提取主服务器的分组名
                group_match = re.search(r'group-title="([^"]+)"', line)
                
                if group_match:
                    current_group = group_match.group(1)
                    # 只要分组属于这 22 个直播分类，就整组搬运
                    if current_group in KEEP_GROUPS:
                        new_m3u.append(lines[i])      # 原始信息行
                        if i + 1 < len(lines):
                            new_m3u.append(lines[i+1]) # 原始 URL 行
                        keep_count += 1
                i += 2 
            else:
                i += 1
                
        # 写入文件
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"处理成功！已保留直播频道: {keep_count} 个。")
        print(f"点播分组已全部从列表中消失。")
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    clean_task()
