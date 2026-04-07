import requests

# 你的原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 整合了所有截图中不想要的分类（黑名单）
EXCLUDE_LIST = [
    "家庭片", "NETFLIX", "奥斯卡 Oscar", "Disney Plus", 
    "记录真人秀", "历史片", "爱情片", "惊悚片", "战争片", 
    "动画片", "喜剧片", "动作片", "科幻片", "奇幻片", "罪案片",
    "轮播LB", "自媒体精选", "TVB剧集", "电影(剧情)", "连续剧(剧情)"
]

def clean_task():
    try:
        print("正在获取数据...")
        res = requests.get(URL, timeout=30)
        # 兼容不同换行符并分割
        lines = res.text.replace('\r', '').split('\n')
        
        new_m3u = ["#EXTM3U"]
        
        i = 0
        count = 0
        while i < len(lines):
            line = lines[i].strip()
            # 找到信息行
            if line.startswith("#EXTINF"):
                # 检查是否包含任何黑名单分类
                is_bad = any(cat in line for cat in EXCLUDE_LIST)
                
                if not is_bad:
                    new_m3u.append(lines[i]) # 保留 #EXTINF 行
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1]) # 保留 URL 行
                else:
                    count += 1
                i += 2 # 无论是否保留，都跳过这一组（信息行+URL行）
            else:
                i += 1
                
        # 保存新文件
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
        print(f"处理完成！删除了 {count} 个点播/电影类频道。")
        print("生成新文件：my_clean_list.m3u")
        
    except Exception as e:
        print(f"出错啦: {e}")

if __name__ == "__main__":
    clean_task()
