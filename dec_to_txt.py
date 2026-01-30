import requests
import json

def start_dec():
    # 37o 核心接口地址
    api_url = "http://ltjm.37o.cc/index.php" 
    
    # --- 以后你只需修改下面这两项 ---
    my_group_name = "我的私人源"  # 这里填你想要的分组名称
    target_url = "这里填入你抓包获取的加密URL" 
    # ----------------------------

    # 以下是根据你的截图 写死的固定参数
    payload = {
        "appname": "XXX直播",
        "packagename": "com.vv.test",
        "sig": "12315",
        "url": target_url, 
        "mac": "c1:bd:92:03:55:bc",        # 固定参数
        "androidid": "5cb5bd4ece1d700c",   # 固定参数
        "model": "TAL-AN000"               # 固定参数
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; TAL-AN000)",
        "Content-Type": "application/json; charset=UTF-8",
        "Referer": "http://ltjm.37o.cc/diyp.php" # 模拟成功页面的入口
    }

    print(f"正在手动解密地址: {target_url}")

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            raw_data = response.text
            
            # 自动生成标准 TXT 分组格式
            txt_format = f"{my_group_name},#genre#\n{raw_data}"
            
            # 保存为 live.txt
            with open("live.txt", "w", encoding="utf-8") as f:
                f.write(txt_format)
            
            print("--- 解密成功，格式已转换 ---")
            print(txt_format)
            print("--------------------------")
        else:
            print(f"解密失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"脚本运行出错: {e}")

if __name__ == "__main__":
    start_dec()
