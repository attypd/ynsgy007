import requests
import re

# 1. 原始接口地址（完全随你的接口变动，不写死分组）
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 2. 必须完整保留的分组（参考你之前发的截图，这些分组里的内容不经过格式过滤，全部保留）
# 包括成人、4K、中文、电影直播等
FAVORITE_GROUPS = [
    "Adults", "三级片", "JP-Uncensored", "惊艳", "4K", 
    "香港 HK", "台湾 TW", "中文(亚洲服务器)", "极限电影"
]

# 3. 点播文件的后缀黑名单
VOD_EXTENSIONS = [".mp4", ".mkv", ".avi", ".rmvb", ".wmv", ".mov"]

def clean_task():
    try:
        print("开始智能扫描：正在通过后缀名识别点播并剔除...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        lines = res.text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 提取分组名和下一行的 URL
                group_match = re.search(r'group-title="([^"]+)"', line)
                current_group = group_match.group(1) if group_match else ""
                
                if i + 1 < len(lines):
                    url_line = lines[i+1].strip().lower()
                    
                    # --- 核心判定逻辑 ---
                    is_keep = False
                    
                    # 逻辑 A：如果你喜欢的成人或核心分组，直接保留
                    if any(fav in current_group for fav in FAVORITE_GROUPS):
                        is_keep = True
                    
                    # 逻辑 B：检查链接后缀，如果是 .mp4 等点播格式，直接踢掉
                    # 只有不是点播格式的（即 .ts, .m3u8 或无后缀直播流），才保留
                    elif not any(url_line.endswith(ext) for ext in VOD_EXTENSIONS):
                        # 额外检查：排除掉带“第X集”或“S01E01”特征的标题
                        if not re.search(r'第\d+集|S\d+E\d+', line):
                            is_keep = True

                    if is_keep:
                        new_m3u.append(lines[i])
                        new_m3u.append(lines[i+1])
                        keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"肃清完成！已保留 {keep_count} 个纯直播频道。")
        print(f"你的成人分组、电影直播等已完整同步。")
        
    except Exception as e:
        print(f"同步失败: {e}")

if __name__ == "__main__":
    clean_task()
