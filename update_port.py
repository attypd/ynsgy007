import requests
import concurrent.futures
import time

# 1. 原有的午夜经典频道
CHANNELS = [
    ("松视3", "SonSee3hd"), ("松视1", "sonsee1"), ("松视2", "sonsee2"),
    ("彩虹e", "RainBowEhd"), ("彩虹k", "RainBowK"), ("彩虹电影", "Rainbowmovie"),
    ("潘多拉", "PandoraWanmei"), ("惊艳成人电影", "Amazingchannel"),
    ("香蕉台", "Bananachannel"), ("happy", "HappyHD"),
    ("极限电影台", "JStarMovies"), ("花花公子", "PlayboyTV"),
    ("日本1", "IdolspecialtychannelPigooHD")
]

# 2. 你抓包提供的所有港台、新马、靖天 ID (新增)
# 格式：(名称, ID参数, 脚本名)
MY_HSTW_LIST = [
    ("佳乐", "JiaLe", "hstw.php"), ("E乐", "ELe", "hstw.php"), ("如意台", "HubRuyi", "hstw.php"),
    ("剧乐酷", "JuLeCool", "hstw.php"), ("娱佳", "HubVVDrama", "hstw.php"), ("都会台", "HubECity", "hstw.php"),
    ("astero1", "Sensasi", "hstw.php"), ("astero2", "AstroWarnaHub", "hstw.php"), ("EnjoyTV5", "EnjoyTV5HD", "hstw.php"),
    ("爱奇艺", "AstroiQIYIFHD", "hstw.php"), ("TVBClassic", "TVBClassicFHDMY", "hstw.php"), ("AstroAECF", "AstroAECFHD", "hstw.php"),
    ("AstroQJ", "AstroQJFHD", "hstw.php"), ("AstroAOD311", "AstroAOD311FHDHK", "hstw.php"), ("TVBjade", "TVBjadeFHDMYHK", "hstw.php"),
    ("CTIAsia", "CTIAsiaFHDMY", "hstw.php"), ("TVBXingHe", "TVBXingHeFHDHK", "hstw.php"), ("采昌", "caichangmovies", "hstw.php"),
    ("新唐人亚太", "NewTangDynasty", "hstw.php"), ("ELTA影剧", "eltamoviedrama", "hstw.php"), ("ELTA日韩", "eltakjdrama", "hstw.php"),
    ("ELTA戏剧", "eyetvdrama", "hstw.php"), ("靖天日本", "JTRBT", "hstw.php"), ("靖天咨询台", "goldentvinfo", "hstw.php"),
    ("靖天国际台", "53", "hstw.php"), ("靖天戏剧台", "goldentvdrama", "hstw.php"), ("靖洋戏剧台", "goldentvforeign", "hstw.php"),
    ("靖天娱乐台", "goldentvyule", "hstw.php"), ("靖天映画台", "goldentvpictures", "hstw.php"), ("靖天欢乐台", "eyetvdrama", "hstw.php"),
    ("CI罪案侦查台", "crimeinvestigation", "hstw.php"), ("亚洲美食", "afn", "hstw.php"), ("CNEK", "cnex", "hstw.php"),
    ("麦哲伦频道", "Magellantv", "hstw.php"), ("原住民频道", "titv", "hstw.php"), ("客家电视台", "hakkatv", "hstw.php"),
    ("中视采青", "ctvbravofhd", "hstw.php"), ("中视经典", "ctvbravofhd", "hstw.php"), ("中视", "ctvhshd", "hstw.php"),
    ("公视", "PTSHD", "hstw.php"), ("公视戏剧", "ptsdrama", "hstw.php"), ("民视", "ftvfhd", "hstw.php"),
    ("公视台语台", "PTS2", "hstw.php"), ("民视第一台", "45", "hstw.php"), ("民视台湾", "37", "hstw.php"),
    ("民视影剧", "ftvmoviedrama", "hstw.php"), ("台视", "TTVHD", "hstw.php"), ("台湾戏剧台", "TaiwanDrama", "hstw.php"),
    ("华视", "ctsfhd", "hstw.php"), ("国兴卫视", "GSTVTW", "hstw.php"), ("TVBS精彩台", "tvbse", "hstw.php"),
    ("TVBS欢乐", "tvbsent", "hstw.php"), ("TVBSHD", "tvbshshd", "hstw.php"), ("八大第一台", "badafirst", "hstw.php"),
    ("八大精彩台", "Badafirst", "hstw.php")
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
    return "44678" # 缺省默认端口

def update_list():
    """该函数负责扫描并生成基础配置文件"""
    port = get_latest_port()
    hstw_base = f"http://url.cdnhs.store:{port}/hstw.php?id="
    lines = ["午夜经典,#genre#"]
    for name, cid in CHANNELS:
        lines.append(f"{name},{hstw_base}{cid}")
    
    bj_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 8*3600))
    lines.append(f"\n# 自动对时: {bj_time}")

    with open("sys_config.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return port # 返回最新端口供后续使用

def harvest_all_extra(port):
    """新增：港台新马合并逻辑，午夜经典强制排在最后"""
    try:
        # 1. 生成港台新马内容
        out = ["🌟港澳台新马,#genre#"]
        for name, cid, api in MY_HSTW_LIST:
            url = f"http://url.cdnhs.store:{port}/{api}?id={cid}"
            out.append(f"{name},{url}")

        # 2. 读取刚才 update_list 生成的午夜内容
        with open("sys_config.txt", "r", encoding="utf-8") as f:
            midnight_data = f.read()

        # 3. 最终合并到 total_live.txt
        # 港台新马在前，午夜经典在后
        with open("total_live.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n\n" + midnight_data)
        print("total_live.txt 已完成全量更新（港台在前，午夜在后）。")
            
    except Exception as e:
        print(f"合并出错: {e}")

if __name__ == "__main__":
    current_port = update_list()      # 获取扫描后的最新端口
    harvest_all_extra(current_port)   # 使用该端口更新全量列表
