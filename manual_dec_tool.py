import requests
import json
import os

def start_dec():
    # 核心接口地址
    api_url = "http://ltjm.37o.cc/index.php" 
    
    # ==========================================
    # 【你手动修改这 3 行，即截图涂鸦位置】
    # ==========================================
    my_app_name = "XXX直播"           # MYlive
    my_package = "com.vv.test"        # com.my.live
    target_url = "这里填登录地址"      # 填入抓包拿到的登录URL
    # =http://api.cdnhs.store/iptv//login3.php

    payload = {
        "appname": my_app_name,
        "packagename": my_package,
        "sig": "12315",                   # 已根据截图写死
        "url": target_url, 
        "mac": "c1:bd:92:03:55:bc",       # 已根据截图写死
        "androidid": "5cb5bd4ece1d700c",  # 已根据截图写死
        "model": "TAL-AN000"              # 已根据截图写死
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; TAL-AN000)",
        "Content-Type": "application/json; charset=UTF-8"
    }

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            raw_data = response.text
            # 转换为 TXT 标准格式：APP名,#genre# + 原始分组数据
            txt_format = f"{my_app_name},#genre#\n{raw_data}"
            
            # 动态命名文件：APP名 + 解密结果.txt
            file_name = f"{my_app_name}解密结果.txt"
            
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(txt_format)
            
            print(f"✅ 执行成功！生成文件：{file_name}")
        else:
            print(f"❌ 接口请求失败，代码: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 出错: {e}")

if __name__ == "__main__":
    start_dec()
