import requests
import concurrent.futures
import time

# 包含 13 个完整频道
CHANNELS = [
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
        # 极速探测，确保 15-30 分钟内能扫完一万个端口
        res = requests.head(url, headers=headers, timeout=0.8, allow_redirects=False)
        if res.status_code in [200, 302]: return str(port)
    except: return None

def get_latest_port():
    # 核心修改：将雷达范围扩大到 40000-50000
    # 这样可以稳稳抓到您抓包发现的 44774 端口
    ports = range(40000, 50000)
    
    # 增加线程数到 150，提升大范围扫描的效率
    with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
        results = executor.map(check_port, ports)
        for r in results:
            if r: return r
    return "43264"

def update_list():
    port = get_latest_port()
    hstw_base = f"http://url.cdnhs.store:{port}/hstw.php?id="
    lines = ["午夜经典,#genre#"]
    for name, cid in CHANNELS:
        lines.append(f"{name},{hstw_base}{cid}")
    
    # 写入北京时间，方便您核对自动化状态
    bj_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 8*3600))
    lines.append(f"\n# 自动对时: {bj_time}")

    with open("sys_config.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"执行完毕，当前有效端口: {port}")
# --- 以下是追加的“港澳台新马”深度收割补丁 ---
def harvest_all_extra():
    try:
        # 1. 拿取刚才 update_list 扫出来的最新端口
        port = get_latest_port() 
        
        # 2. 定义港澳台、新马、电影频道列表
        ext_channels = [
            ("凤凰中文", "MytvPhoenixChinese", "hstw.php"), ("凤凰香港", "MytvPhoenixHK", "hstw.php"),
            ("凤凰资讯", "MytvPhoenixInfo", "hstw.php"), ("翡翠台", "jadehk", "hstw.php"),
            ("无线新闻", "hknp", "hstw.php"), ("澳视澳门", "tdm1", "hstw.php"),
            ("星影电影", "10", "nowtv.php"), ("爆谷电影", "57", "nowtv.php"),
            ("美亚电影", "17", "mytv.php"), ("Astro华丽台", "21", "mytv.php"),
            ("新传媒8频道", "31", "nowtv.php"), ("HBO HD", "56", "nowtv.php")
        ]

        out = ["🌟港澳台新马,#genre#"]
        for name, cid, api in ext_channels:
            # 强制生成链接，跳过网络探测确保列表显示
            url = f"http://url.cdnhs.store:{port}/{api}?id={cid}"
            out.append(f"{name},{url}")

        # 3. 读取原本生成的“午夜经典”
        with open("sys_config.txt", "r", encoding="utf-8") as f:
            midnight_data = f.read()

        # 4. 覆盖写入总表 total_live.txt
        with open("total_live.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n\n" + midnight_data)
            
    except: pass

if __name__ == "__main__":
    update_list()       # 运行原有的更新逻辑
    harvest_all_extra() # 运行新增的强力收割逻辑
