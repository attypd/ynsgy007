import requests
import concurrent.futures
import time

# 1. 港澳台新马全量 ID 库 (严格校对 ID 与 路径)
HSTW_LIST = [
    # 凤凰与港澳
    ("凤凰中文", "MytvPhoenixChinese", "hstw.php"), ("凤凰香港", "MytvPhoenixHK", "hstw.php"),
    ("凤凰资讯", "MytvPhoenixInfo", "hstw.php"), ("翡翠台", "jadehk", "hstw.php"),
    ("无线新闻", "hknp", "hstw.php"), ("澳视澳门", "tdm1", "hstw.php"),
    # 星马系列
    ("佳乐", "JiaLe", "hstw.php"), ("E乐", "ELe", "hstw.php"),
    ("如意台", "HubRuyi", "hstw.php"), ("剧乐酷", "JuLeCool", "hstw.php"),
    ("娱佳", "HubVVDrama", "hstw.php"), ("都会台", "HubECity", "hstw.php"),
    ("astero1", "Sensasi", "hstw.php"), ("astero2", "AstroWarnaHub", "hstw.php"),
    ("EnjoyTV5", "EnjoyTV5HD", "hstw.php"), ("爱奇艺", "AstroiQIYIFHD", "mytv.php"),
    ("TVBClassic", "TVBClassicFHDMY", "hstw.php"), ("AstroAECF", "AstroAECFHD", "hstw.php"),
    ("AstroQJ", "AstroQJFHD", "hstw.php"), ("AstroAOD311", "AstroAOD311FHDHK", "hstw.php"),
    ("TVBjade", "TVBjadeFHDMYHK", "hstw.php"), ("CTIAsia", "CTIAsiaFHDMY", "hstw.php"),
    ("TVBXingHe", "TVBXingHeFHDHK", "hstw.php"), ("采昌", "caichangmovies", "hstw.php"),
    ("新唐人亚太", "NewTangDynasty", "hstw.php"), ("ELTA影剧", "eltamoviedrama", "hstw.php"),
    ("ELTA日韩", "eltakjdrama", "hstw.php"), ("ELTA戏剧", "eyetvdrama", "hstw.php"),
    ("靖天日本", "JTRBT", "hstw.php"), ("靖天咨询台", "goldentvinfo", "hstw.php"),
    ("靖天国际台", "53", "hstw.php"), ("靖天戏剧台", "goldentvdrama", "hstw.php"),
    ("靖洋戏剧台", "goldentvforeign", "hstw.php"), ("靖天娱乐台", "goldentvyule", "hstw.php"),
    ("靖天映画台", "goldentvpictures", "hstw.php"), ("靖天欢乐台", "eyetvdrama", "hstw.php"),
    ("CI罪案侦查台", "crimeinvestigation", "hstw.php"), ("亚洲美食", "afn", "hstw.php"),
    ("CNEK", "cnex", "hstw.php"), ("麦哲伦频道", "Magellantv", "hstw.php"),
    ("原住民频道", "titv", "hstw.php"), ("客家电视台", "hakkatv", "hstw.php"),
    # 台湾系列
    ("中视采青", "ctvbravofhd", "hstw.php"), ("中视经典", "ctvclassic", "hstw.php"),
    ("中视", "ctvhshd", "hstw.php"), ("公视", "PTSHD", "hstw.php"),
    ("公视戏剧", "ptsdrama", "hstw.php"), ("民视", "ftvfhd", "hstw.php"),
    ("公视台语台", "PTS2", "hstw.php"), ("民视第一台", "45", "hstw.php"),
    ("民视台湾", "37", "hstw.php"), ("民视影剧", "ftvmoviedrama", "hstw.php"),
    ("台视", "TTVHD", "hstw.php"), ("台湾戏剧台", "TaiwanDrama", "hstw.php"),
    ("华视", "ctsfhd", "hstw.php"), ("国兴卫视", "GSTVTW", "hstw.php"),
    ("TVBS精彩台", "tvbse", "hstw.php"), ("TVBS欢乐", "tvbsent", "hstw.php"),
    ("TVBSHD", "tvbshshd", "hstw.php"), ("八大第一台", "badafirst", "hstw.php"),
    ("八大精彩台", "Badafirst", "hstw.php"),
    # 电影与特殊频道 (重点校对区)
    ("星影电影", "10", "nowtv.php"), 
    ("爆谷电影", "57", "nowtv.php"),
    ("美亚电影", "17", "mytv.php"), 
    ("Astro华丽台", "21", "mytv.php"),
    ("新传媒8频道", "31", "nowtv.php"), 
    ("HBO HD", "56", "nowtv.php")
]

# 2. 午夜经典 (原始核心)
MIDNIGHT_CHANNELS = [
    ("松视3", "SonSee3hd"), ("松视1", "sonsee1"), ("松视2", "sonsee2"),
    ("彩虹e", "RainBowEhd"), ("彩虹k", "RainBowK"), ("彩虹电影", "Rainbowmovie"),
    ("潘多拉", "PandoraWanmei"), ("惊艳成人电影", "Amazingchannel"),
    ("香蕉台", "Bananachannel"), ("happy", "HappyHD"),
    ("极限电影台", "JStarMovies"), ("花花公子", "PlayboyTV"),
    ("日本1", "IdolspecialtychannelPigooHD")
]

def check_port(port):
    headers = {'User-Agent': 'mitv', 'Range': 'bytes=0-'}
    url = f"http://url.cdnhs.store:{port}/hstw.php?id=SonSee3hd"
    try:
        res = requests.head(url, headers=headers, timeout=0.8, allow_redirects=False)
        if res.status_code in [200, 302]: return str(port)
    except: return None

def get_latest_port():
    ports = range(40000, 50000)
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        results = executor.map(check_port, ports)
        for r in results:
            if r: return r
    return "44678"

def update_all():
    port = get_latest_port()
    base_url = f"http://url.cdnhs.store:{port}"
    
    # --- 生成 sys_config.txt (只留午夜经典) ---
    midnight_lines = ["午夜经典,#genre#"]
    for name, cid in MIDNIGHT_CHANNELS:
        midnight_lines.append(f"{name},{base_url}/hstw.php?id={cid}")
    
    bj_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 8*3600))
    midnight_lines.append(f"\n# 自动对时: {bj_time}")
    
    with open("sys_config.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(midnight_lines))

    # --- 生成 total_live.txt (全量合并，校对星影/爆谷/HBO) ---
    total_lines = ["🌟港澳台新马,#genre#"]
    for name, cid, api in HSTW_LIST:
        total_lines.append(f"{name},{base_url}/{api}?id={cid}")
    
    total_lines.append("\n" + "\n".join(midnight_lines))
    
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(total_lines))
    
    print(f"校对更新完成！当前端口: {port}")

if __name__ == "__main__":
    update_all()
