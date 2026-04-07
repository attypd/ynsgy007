import requests
import re

# 1. 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 2. 直播分组白名单（根据你的 8 张截图锁定）
# 只要原始接口中 group-title 等于下面这些，里面的频道一律原样保留
LIVE_GROUPS = [
    "4K", "香港 HK", "台湾 TW", "大陆 CN", "海外中文 OC", "马来 MY", "日本 JP", 
    "韩国 KR", "英国 UK", "美国 US", "法国 FR", "加拿大 CA", "澳洲 AU", 
    "泰国 TH", "越南 VN", "菲律宾 PH", "印度 India",
    "Sports", "News", "Documentary", "Music", "Kids", 
    "中文(亚洲服务器)"
]

def clean_task():
    try:
        print("正在执行智能识别：保留原味直播，剔除冗余点播...")
        # 增加超时时间至 60 秒，确保大体积原始接口下载不中断
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8' 
        
        content = res.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 识别频道描述行
            if line.startswith("#EXTINF"):
                # 动态提取原始分组名称
                group_match = re.search(r'group-title="([^"]+)"', line)
                
                if group_match:
                    current_group = group_match.group(1)
                    
                    # 核心智能逻辑：只允许白名单中的直播分组通过
                    # 这样可以完美避开那些成千上万、导致配置失败的点播分组
                    if current_group in LIVE_GROUPS:
                        new_m3u.append(lines[i])      # 原始描述
                        if i + 1 < len(lines):
                            new_m3u.append(lines[i+1]) # 原始播放地址
                        keep_count += 1
                
                i += 2 
            else:
                i += 1
                
        # 生成你自己的纯净直播源文件
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"--- 处理成功 ---")
        print(f"已动态同步保留了 {keep_count} 个原始直播频道。")
        print(f"点播分组已按要求全数剔除，现在文件体积非常小。")
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    clean_task()
