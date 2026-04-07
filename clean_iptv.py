import requests

# 1. 原始接口地址（随主服务器动态同步）
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 2. 定义绝对不要的“点播库”关键词
# 只要分组名里带了这些词，就是那种几万个文件的点播，直接踢掉
# 剩下的直播分组（不管是叫 4K、香港、中文，还是新出的直播组）全部原封不动保留
VOD_KEYWORDS = [
    "NETFLIX", "奥斯卡", "Disney", "Netflix", "电影", "连续剧", "剧情", 
    "惊悚", "战争", "动画", "喜剧", "动作", "科幻", "奇幻", "罪案", "历史", 
    "爱情", "轮播", "精选", "Adults", "Adult", "三级片", "JP-Uncensored"
]

def clean_task():
    try:
        print("正在从主服务器同步所有直播分组（已智能剔除点播库）...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        lines = res.text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 检查这一行是否属于点播分组
                is_vod = any(kw.lower() in line.lower() for kw in VOD_KEYWORDS)
                
                # 核心逻辑：如果是直播电影台（比如属于“亚洲服务器”的分组），它们通常不带上面那些垃圾词
                # 只要不是点播，就原样搬运
                if not is_vod:
                    new_m3u.append(lines[i])      # 原始信息
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1]) # 原始播放链接
                    keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"同步完成！已原样保留了 {keep_count} 个直播频道。")
        print("所有直播分组（包括 4K、中文、体育及新增直播类）已按原始结构同步。")
        
    except Exception as e:
        print(f"同步失败: {e}")

if __name__ == "__main__":
    clean_task()
