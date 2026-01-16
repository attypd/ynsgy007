import requests
import concurrent.futures
import time

# 1. 你抓包的所有港台新马 ID (置顶)
MY_HSTW_LIST = [
    ("凤凰中文", "MytvPhoenixChinese"), ("凤凰香港", "MytvPhoenixHK"), ("凤凰资讯", "MytvPhoenixInfo"),
    ("翡翠台", "jadehk"), ("无线新闻", "hknp"), ("澳视澳门", "tdm1"),
    ("佳乐", "JiaLe"), ("E乐", "ELe"), ("如意台", "HubRuyi"), ("剧乐酷", "JuLeCool"),
    ("娱佳", "HubVVDrama"), ("都会台", "HubECity"), ("TVBClassic", "TVBClassicFHDMY"),
    ("TVBjade", "TVBjadeFHDMYHK"), ("CTIAsia", "CTIAsiaFHDMY"), ("TVBXingHe", "TVBXingHeFHDHK"),
    ("采昌", "caichangmovies"), ("新唐人亚太", "NewTangDynasty"), ("ELTA影剧", "eltamoviedrama"),
    ("ELTA日韩", "eltakjdrama"), ("ELTA戏剧", "eyetvdrama"), ("靖天日本", "JTRBT"),
    ("靖天戏剧台", "goldentvdrama"), ("靖洋戏剧台", "goldentvforeign"), ("靖天娱乐台", "goldentvyule"),
    ("中视", "ctvhshd"), ("公视", "PTSHD"), ("民视", "ftvfhd"), ("台视", "TTVHD"),
    ("华视", "ctsfhd"), ("TVBS精彩台", "tvbse"), ("TVBS欢乐", "tvbsent"), ("TVBSHD", "tvbshshd")
]

# 2. 午夜经典频道 (保持原始 ID)
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
    hstw_base = f"http://url.cdnhs.store:{port}/hstw.php?id="
    
    # 构建最终内容
    lines = ["🌟港澳台新马,#genre#"]
    # 添加港台新马
    for name, cid in MY_HSTW_LIST:
        lines.append(f"{name},{hstw_base}{cid}")
    
    # 特殊处理电影 ID (这些可能使用 nowtv.php 或 mytv.php)
    lines.append("星影电影,http://url.cdnhs.store:" + port + "/nowtv.php?id=10")
    lines.append("爆谷电影,http://url.cdnhs.store:" + port + "/nowtv.php?id=57")
    lines.append("美亚电影,http://url.cdnhs.store:" + port + "/mytv.php?id=17")

    # 添加午夜经典
    lines.append("\n午夜经典,#genre#")
    for name, cid in MIDNIGHT_CHANNELS:
        lines.append(f"{name},{hstw_base}{cid}")
    
    # 写入北京时间
    bj_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 8*3600))
    lines.append(f"\n# 自动对时: {bj_time}")

    final_content = "\n".join(lines)
    
    # 物理更新两个文件
    for filename in ["total_live.txt", "sys_config.txt"]:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(final_content)
    
    print(f"执行完毕！最新有效端口: {port}")

if __name__ == "__main__":
    update_all()
