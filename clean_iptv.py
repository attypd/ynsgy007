import requests
import re

# 1. 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 2. 【点播分组名单】：完全对应你截图里要删掉的每一个点播组名字
# 只要不是这名单里的，哪怕是新加的分组也会自动保留
DELETE_GROUPS = [
    "轮播LB", "自媒体精选", "喜剧片", "惊悚片", "动作片", "动画片", 
    "战争片", "爱情片", "奇幻片", "科幻片", "罪案片", "家庭片", 
    "历史片", "电影(剧情)", "连续剧(剧情)", "TVB 剧集", "纪录真人秀", 
    "NETFLIX", "Disney Plus", "奥斯卡 Oscar"
]

def clean_task():
    try:
        print("正在按截图列表剔除点播分组，保留所有直播及传媒频道...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        lines = res.text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 提取分组名
                group_match = re.search(r'group-title="([^"]+)"', line)
                current_group = group_match.group(1) if group_match else ""
                
                # --- 严格匹配逻辑 ---
                # 只有当分组名【完全等于】名单里的名字时，才删除
                if current_group in DELETE_GROUPS:
                    i += 2 # 直接跳过这组的 INF 和 URL
                    continue
                
                # 此外，根据你的要求，后缀是 .mp4 的点播也顺带过滤掉，双重保险
                if i + 1 < len(lines):
                    url_line = lines[i+1].strip().lower()
                    if url_line.endswith(".mp4"):
                        i += 2
                        continue

                # 剩下的全部保留（包括传媒组、所有直播组、未来新增组）
                new_m3u.append(lines[i])
                new_m3u.append(lines[i+1])
                keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"肃清完成！")
        print(f"已严格剔除截图中的点播组。")
        print(f"当前保留直播源总数: {keep_count}")
        
    except Exception as e:
        print(f"运行失败: {e}")

if __name__ == "__main__":
    clean_task()
