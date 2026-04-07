import requests

# 你的原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 更加全面的黑名单关键字（只要分类名包含这些词，就剔除）
EXCLUDE_KEYWORDS = [
    "家庭", "NETFLIX", "奥斯卡", "Disney", "Netflix",
    "真人秀", "历史", "爱情", "惊悚", "战争", "动画", 
    "喜剧", "动作", "科幻", "奇幻", "罪案", "电影",
    "轮播", "精选", "TVB", "连续剧", "剧情"
]

def clean_task():
    try:
        print("正在获取并深度清理直播源...")
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
                # 深度检查：只要当前行包含黑名单里的任何一个词，就标记为“坏频道”
                is_bad = any(kw in line for kw in EXCLUDE_KEYWORDS)
                
                if not is_bad:
                    # 如果是好频道，保留这一行和它下面紧跟的 URL 行
                    new_m3u.append(lines[i])
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1])
                else:
                    count += 1
                
                # 步进 2 行（跳过已经处理的一组数据）
                i += 2
            else:
                i += 1
                
        # 保存精简后的结果
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"清理完成！共剔除了 {count} 个非直播频道。")
        print("最新文件已生成：my_clean_list.m3u")
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    clean_task()
