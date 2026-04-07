import requests

# 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 绝对不要的点播分组关键词（只要分组名包含这些，通通删掉）
# 加上了你刚截图的 "TVB 剧集" 和 "家庭片"
DISCARD_KEYWORDS = [
    "TVB 剧集", "家庭片", "纪录真人秀", # 针对你最新截图的分组
    "NETFLIX", "Disney", "Netflix", "奥斯卡", 
    "电影", "连续剧", "成人", "Adult", "三级", "福利"
]

def clean_task():
    try:
        print("正在微调：精准剔除 TVB 剧集与家庭片等点播分组...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        lines = res.text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 检查分组名是否包含黑名单关键词
                # 只要包含 "TVB 剧集" 或 "家庭片"，就把 is_vod 设为 True
                is_vod = any(kw.lower() in line.lower() for kw in DISCARD_KEYWORDS)
                
                # 额外逻辑：自动识别带 S01E01 这种剧集编号的行（双重保险）
                is_series = "s0" in line.lower() and "e0" in line.lower()

                # 只有既不是黑名单，也不带剧集编号的，才保留
                if not is_vod and not is_series:
                    new_m3u.append(lines[i])      # 原始信息
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1]) # 原始 URL
                    keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"微调同步完成！")
        print(f"已成功屏蔽“TVB 剧集”和“家庭片”等冗余点播。")
        print(f"当前保留直播频道总数: {keep_count}")
        
    except Exception as e:
        print(f"运行失败: {e}")

if __name__ == "__main__":
    clean_task()
