import requests

# 你的原始接口
URL = "http://iptvpro.pw:35451/get.php?username=3582251457&password=4975354955&type=m3u_plus&output=ts"

# 截图里不想要的分类
EXCLUDE_LIST = [
    "家庭片", "NETFLIX", "奥斯卡 Oscar", "Disney Plus", 
    "记录真人秀", "历史片", "爱情片", "惊悚片", "战争片", 
    "动画片", "喜剧片", "动作片", "科幻片", "奇幻片", "罪案片"
]

def clean_task():
    try:
        res = requests.get(URL, timeout=30)
        lines = res.text.split('\n')
        new_m3u = ["#EXTM3U"]
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#EXTINF"):
                if not any(cat in line for cat in EXCLUDE_LIST):
                    new_m3u.append(lines[i])
                    if i + 1 < len(lines):
                        new_m3u.append(lines[i+1])
                i += 2
            else:
                i += 1
        with open("my_clean_list.m3u", "w", encoding="utf-8") as f:
            f.write('\n'.join(new_m3u))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean_task()
