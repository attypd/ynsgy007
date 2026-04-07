import requests
import re

# 原始接口地址
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 1. 【保命白名单】：只要频道名字里带这些词，不管它在哪个组，通通保留！
# 这样能确保“电影频道”、“极限电影”、“HBO电影”等直播台不被误删
KEEP_KEYWORDS = ["电影频道", "极限电影", "电影台", "HBO", "星卫", "卫视电影"]

# 2. 【必杀黑名单】：只要分组名命中这些，且不在保命名单里的，全部剔除
DISCARD_GROUPS = [
    "轮播", "自媒体", "喜剧片", "惊悚片", "动作片", "动画片", "战争片", 
    "爱情片", "奇幻片", "科幻片", "罪案片", "纪录真人秀", "TVB 剧集", 
    "历史片", "家庭片", "电影", "连续剧", "SWAG", "成人", "Adult"
]

# 3. 【特征识别】：识别点播文件的典型特征
VOD_PATTERNS = [
    r"S\d+E\d+",      # 匹配 S01E01
    r"第\d+集",        # 匹配 第1集
    r"\[SWAG\]",      # 匹配 [SWAG]
    r"^\d{4}\s",      # 匹配 1314 这种纯数字开头的点播编号
]

def clean_task():
    try:
        print("正在精细化过滤：保住电影直播台，清除点播垃圾...")
        res = requests.get(URL, timeout=60)
        res.encoding = 'utf-8'
        lines = res.text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        new_m3u = ["#EXTM3U"]
        i = 0
        keep_count = 0
        
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                # 提取关键信息
                group_match = re.search(r'group-title="([^"]+)"', line)
                current_group = group_match.group(1) if group_match else ""
                channel_title = line.split(',')[-1] if ',' in line else ""

                # --- 核心判定逻辑 ---
                is_keep = False
                
                # 第一步：检查保命白名单（最高优先级）
                if any(kw in channel_title for kw in KEEP_KEYWORDS):
                    is_keep = True
                
                # 第二步：如果不在白名单，检查是否属于点播分组或带点播特征
                if not is_keep:
                    # 检查分组名
                    is_discard_group = any(kw in current_group for kw in DISCARD_GROUPS)
                    # 检查标题特征（如西游记 1315）
                    is_vod_feature = any(re.search(p, channel_title, re.IGNORECASE) for p in VOD_PATTERNS)
                    
                    if not is_discard_group and not is_vod_feature:
                        is_keep = True

                # --- 执行保留 ---
                if is_keep:
                    new_m3u.append(lines[i])
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1])
                    keep_count += 1
                i += 2 
            else:
                i += 1
                
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
            
        print(f"处理完成！已成功保住电影直播台，当前保留频道总数: {keep_count}")
        
    except Exception as e:
        print(f"运行失败: {e}")

if __name__ == "__main__":
    clean_task()
