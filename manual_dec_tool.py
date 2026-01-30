import requests
import json
import os

def start_dec():
    # 核心接口地址
    api_url = "http://ltjm.37o.cc/index.php" 
    
    # ==========================================
    # 【你只改这 3 行涂鸦位置】
    # ==========================================
    my_app_name = "MYlive"           
    my_package = "com.my.live"        
    target_url = "http://api.cdnhs.store/iptv//login3.php"    
    # ==========================================

    payload = {
        "appname": my_app_name,
        "packagename": my_package,
        "sig": "12315",                   
        "url": target_url, 
        "mac": "c1:bd:92:03:55:bc",       
        "androidid": "5cb5bd4ece1d700c",  
        "model": "TAL-AN000"              
    }

    # 🚨 这里的加强伪装是解决 403 的关键
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; TAL-AN000 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.141 Mobile Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Referer": "http://ltjm.37o.cc/", 
        "Origin": "http://ltjm.37o.cc",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers, timeout=15)
        
        # 调试信息：看看返回了什么
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            raw_data = response.text
            if "http" in raw_data: # 确保拿到了链接
                txt_format = f"{my_app_name},#genre#\n{raw_data}"
                file_name = f"{my_app_name}解密结果.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(txt_format)
                print(f"✅ 执行成功！已生成：{file_name}")
            else:
                print(f"❌ 解密内容异常，返回结果：{raw_data}")
        else:
            print(f"❌ 接口请求失败，代码: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ 出错: {e}")

if __name__ == "__main__":
    start_dec()
