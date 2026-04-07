import requests

# 你的原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 1. 白名单：即便包含黑名单关键词也要强制保留的词
INCLUDE_KEYWORDS = ["极限电影", "JStar"]

# 2. 黑名单：依然需要屏蔽的关键词
EXCLUDE_KEYWORDS = [
    "家庭", "NETFLIX", "奥斯卡", "Disney", "Netflix",
    "真人秀", "历史", "爱情", "惊悚", "战争", "动画", 
    "喜剧", "动作", "科幻", "奇幻", "罪案", "电影",
    "轮播", "精选", "TVB", "连续剧", "剧情"
]

def clean_task():
    try:
        print("正在获取并精简直播源（特赦极限电影台）...")
        res = requests.get(URL, timeout=30)
        # 统一换行符
        content = res.text.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')
        
        new_m3u = ["#EXTM3U"]
        
        i = 0
        count = 0
        while i < len(lines):
            line = lines[i].strip()
            # 找到信息行 #EXTINF
            if line.startswith("#EXTINF"):
                # --- 修改后的逻辑 ---
                # A. 首先检查是否命中“白名单”（如：极限电影）
                is_white = any(kw in line for kw in INCLUDE_KEYWORDS)
                
                if is_white:
                    # 如果是白名单频道，直接保留
                    new_m3u.append(lines[i])
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1])
                else:
                    # B. 如果不是白名单，再检查是否包含黑名单词汇
                    is_bad = any(kw in line for kw in EXCLUDE_KEYWORDS)
                    
                    if not is_bad:
                        # 既不在白名单也不在黑名单的频道，正常保留
                        new_m3u.append(lines[i])
                        if i + 1 < len(lines):
                            new_m3u.append(lines[i+1])
                    else:
                        count += 1
                
                # 步进 2 行
                i += 2
            else:
                i += 1
                
        # 保存结果
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"清理完成！剔除了 {count} 个非直播频道，已保留极限电影台。")
        print("最新文件已生成：my_clean_list.m3u")
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    clean_task()
