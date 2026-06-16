"""
Locket Friend Spam Tool - Python 3 (Bản sửa lỗi không hiện lời mời - dùng request chuẩn và token mới)
"""

import requests
import json
import time
import random
import re
from urllib.parse import urlparse

# ============================================
# CẤU HÌNH
# ============================================
BASE_URL = "https://api.locketcamera.com"
SEARCH_ENDPOINT = "/getUserByUsername"

# ============================================
# REQUEST CHUẨN TỪ STREAM (ĐÃ CẬP NHẬT)
# ============================================
# Endpoint gửi lời mời từ request chuẩn của bạn
FRIEND_REQUEST_ENDPOINT = "/v1/friends/requests"

# Body mẫu - dùng __USER_ID__ làm placeholder
# QUAN TRỌNG: Bạn cần cung cấp BODY thực tế từ request trong Stream
# Đây là nơi cần sửa để tool hoạt động chính xác
FRIEND_REQUEST_BODY_TEMPLATE = {
    "userId": "__USER_ID__",        # <--- SỬA THEO BODY THỰC TẾ
    "source": "search"              # Thêm source nếu có trong body chuẩn
}

# Phương thức
FRIEND_REQUEST_METHOD = "POST"

# Header bổ sung (nếu request chuẩn có header đặc biệt)
EXTRA_HEADERS = {
    # "X-Request-ID": "giá trị",
    # "X-Platform": "ios"
}

# ============================================
# TOKEN MỚI (CẬP NHẬT TỪ REQUEST CỦA BẠN)
# ============================================
AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImVlOTA0NmVhZDJlMDUwMDAxMGVkNTA0M2I0ODNkODRiMGM1MmM3YzQiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiQm8gRGVwWmFpIiwicmV2ZW51ZUNhdEVudGl0bGVtZW50cyI6W10sImlzcyI6Imh0dHBzOi8vc2VjdXJldG9rZW4uZ29vZ2xlLmNvbS9sb2NrZXQtNDI1MmEiLCJhdWQiOiJsb2NrZXQtNDI1MmEiLCJhdXRoX3RpbWUiOjE3ODE2MzA4NzMsInVzZXJfaWQiOiJwVEcxSEhvck5ZZVFlUVFmaEV4dnBwNVJ1MDMzIiwic3ViIjoicFRHMUhIb3JOWWVRZVFRZmhFeHZwcDVSdTAzMyIsImlhdCI6MTc4MTYzMDg3MywiZXhwIjoxNzgxNjM0NDczLCJlbWFpbCI6Im1pbmh0aGllbjIyMDYyMDExQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJtaW5odGhpZW4yMjA2MjAxMUBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.u1_vER02KWf6oQ3KgI2_UsJ6Mcux0BmhL2F4LZ_lW8EqJRlC1yx_vlysuJj5dvyhGLDoFCo-BiKAGppsIJbelcoSkV1HU0enkqUAunE1IrRGRfKK5DmGmxYX3ApLs2o3SmwEF2soByWXnEmygZ-sOcxCZ_OoxZ4-RPyYpHzOc-CrMXdVVO4mOOZS3ZTlwUrA_zETUW6-Q2C8PjiyT4blq4OvlViYFNxGJQEO1nO3RMJxLJ0Q8SCowd-wl4KhJ01b2cZI7lqnpzFznleSeB17qnLiILwNx0ub9-ntuBdXxIgP9IWzAgj_ZViRealbU6yrPPdcGsFZh-XiIFxzL88W6w"

# ============================================
# HEADER CỐ ĐỊNH
# ============================================
USER_AGENT = "com.locket.Locket/2.51.0 iPhone/26.3.1 hw/iPhone12_3"
ACCEPT_LANGUAGE = "vi-VN,vi;q=0.9"
ACCEPT_ENCODING = "gzip, deflate, br"
CONNECTION = "keep-alive"
HOST = "api.locketcamera.com"
CONTENT_TYPE = "application/json"

# Các header khác (lấy từ request chuẩn)
FIREBASE_APP_CHECK = "eyJraWQiOiJrMnhhbUEiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxOjY0MTAyOTA3NjA4Mzppb3M6Y2M4ZWI0NjI5MGQ2OWIyMzRmYTYwNiIsImF1ZCI6WyJwcm9qZWN0cy82NDEwMjkwNzYwODMiLCJwcm9qZWN0cy9sb2NrZXQtNDI1MmEiXSwicHJvdmlkZXIiOiJkZXZpY2VfY2hlY2tfZGV2aWNlX2lkZW50aWZpY2F0aW9uIiwiaXNzIjoiaHR0cHM6Ly9maXJlYmFzZWFwcGNoZWNrLmdvb2dsZWFwaXMuY29tLzY0MTAyOTA3NjA4MyIsImV4cCI6MTc4MTYzMTIyMiwiaWF0IjoxNzgxNjI3NjIyLCJqdGkiOiJFVmpYYlpYREducEtiV3l0UTQycEVQZlRYVlhfV1ZNN1hvUlpPTkpyeWswIn0.xxRXvWsoZHrXdaQ-fl1CxpmdtcQ5qSncw5CwTd8azeAoE8A7kMC3dTzpmNa5Drvf9BR0k-0Igf4cb6OpuCcVc9-2kVcR05PCFp_OlIcJi8OcEDDP6R8qk-D7zRz8YbklZ7-ah1XiWoTEzg7r9Zhla-wNCekCO0mrbOWYfXJjb53X50_c0a9zVxb5S1A6h3g-yeW8RIwG8YLUywjG0tVpyEI3gq_8l0hEPkL1bwo2S5WKmGLDpAoKghuekzNv5dEL2ZmhQezDFjz4aHSYzGqHYnFauga_50rLvNA2mRflnCEuNZ0PONPWPzQ233cgrzPEwXjBDBIMV21Lv2gaM5XVHNV9Ne4CP_8IWmicXNYgI6Xrqn7ZUkrgzgpi4sFI5jI-0BfI_IEHCxh9uPzMPsM-bfEYN4iceYYJi1ekeJUKLYPObjNvZ63istvFaa9IES2McDzmJOPCG5r68uIcm9vvj4RmHRCwWSCCaYeamW2XRtRitM-sWLO4U2NyR0ZfKzwq"
FIREBASE_INSTANCE_ID = "dhbFbJNPE00FuTSWpo2A2r:APA91bEBNvK4VnsPuMCuUSVxEBtoVEdWeEiTkT047UN4h_U4J05NrCy1xfUo-EFswrUjlkXe-GqQaXCCb0HbYHCADVaPe1fMTkSdLmySpcb7lZMYdgURJ3U"
SENTRY_TRACE = "7d76e42133be40f48d7c5fe043e031ba-fd6b0aad5a034f14-0"
BAGGAGE = "sentry-environment=production,sentry-public_key=78fa64317f434fd89d9cc728dd168f50,sentry-release=com.locket.Locket%402.51.0%2B1,sentry-trace_id=7d76e42133be40f48d7c5fe043e031ba"

# ============================================
# CLASS CHÍNH
# ============================================
class LocketSpamTool:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Host": HOST,
            "Accept": "*/*",
            "Accept-Language": ACCEPT_LANGUAGE,
            "Accept-Encoding": ACCEPT_ENCODING,
            "Content-Type": CONTENT_TYPE,
            "Connection": CONNECTION,
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "X-Firebase-AppCheck": FIREBASE_APP_CHECK,
            "Firebase-Instance-ID-Token": FIREBASE_INSTANCE_ID,
            "sentry-trace": SENTRY_TRACE,
            "baggage": BAGGAGE
        })
        # Thêm header bổ sung
        for key, value in EXTRA_HEADERS.items():
            self.session.headers[key] = value
            
        self.target_user_id = None
        self.target_username = None
        self.retry_count = 0

    # ============================================
    # HÀM TÌM KIẾM USERNAME
    # ============================================
    def search_username(self, username_or_link):
        if "locketcamera.com" in username_or_link or "locket" in username_or_link:
            parsed = urlparse(username_or_link)
            path_parts = parsed.path.split('/')
            username_or_link = path_parts[-1] if path_parts[-1] else path_parts[-2]
        
        print(f"\n[+] Đang tìm kiếm: {username_or_link}")
        
        search_url = f"{BASE_URL}{SEARCH_ENDPOINT}"
        
        payloads = [
            {"username": username_or_link},
            {"data": {"username": username_or_link}}
        ]
        
        for payload in payloads:
            try:
                response = self.session.post(search_url, json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Xử lý response linh hoạt
                    user_data = None
                    
                    # Dạng 1: result.data.uid
                    if data.get("result") and data["result"].get("data") and data["result"]["data"].get("uid"):
                        user_data = data["result"]["data"]
                        self.target_user_id = user_data.get("uid")
                        first_name = user_data.get("first_name", "")
                        last_name = user_data.get("last_name", "")
                        self.target_username = f"{first_name} {last_name}".strip()
                        print(f"[+] Tìm thấy: {self.target_username} (ID: {self.target_user_id})")
                        return True
                    
                    # Dạng 2: user
                    elif data.get("user"):
                        user_data = data["user"]
                        self.target_user_id = user_data.get("id")
                        self.target_username = user_data.get("username") or user_data.get("name") or "unknown"
                        print(f"[+] Tìm thấy: {self.target_username} (ID: {self.target_user_id})")
                        return True
                    
                    # Dạng 3: data.user
                    elif data.get("data") and data["data"].get("user"):
                        user_data = data["data"]["user"]
                        self.target_user_id = user_data.get("id")
                        self.target_username = user_data.get("username") or user_data.get("name") or "unknown"
                        print(f"[+] Tìm thấy: {self.target_username} (ID: {self.target_user_id})")
                        return True
                    
                    # Dạng 4: id trực tiếp
                    elif data.get("id"):
                        self.target_user_id = data.get("id")
                        self.target_username = data.get("username") or data.get("name") or "unknown"
                        print(f"[+] Tìm thấy: {self.target_username} (ID: {self.target_user_id})")
                        return True
                    
                    else:
                        print(f"[-] Không tìm thấy user. Response: {json.dumps(data, indent=2)[:300]}")
                        return False
                
                elif response.status_code == 400:
                    continue
                else:
                    print(f"[-] Lỗi API: {response.status_code} - {response.text[:200]}")
                    return False
                    
            except Exception as e:
                print(f"[-] Lỗi kết nối: {e}")
                continue
        
        return False

    # ============================================
    # HÀM GỬI LỜI MỜI - CHÍNH XÁC THEO REQUEST CHUẨN
    # ============================================
    def send_friend_request(self, user_id):
        """
        Gửi lời mời kết bạn - dùng endpoint và body từ request chuẩn
        """
        endpoint = f"{BASE_URL}{FRIEND_REQUEST_ENDPOINT}"
        
        # Tạo body từ template
        body = {}
        for key, value in FRIEND_REQUEST_BODY_TEMPLATE.items():
            if isinstance(value, str) and "__USER_ID__" in value:
                body[key] = value.replace("__USER_ID__", user_id)
            else:
                body[key] = value
        
        # Thử gửi request
        try:
            print(f"[DEBUG] Gửi request tới: {endpoint}")
            print(f"[DEBUG] Body: {json.dumps(body)}")
            
            response = self.session.post(endpoint, json=body, timeout=15)
            
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response body: {response.text[:200]}")
            
            if response.status_code in [200, 201, 204]:
                return True, "Thành công"
            elif response.status_code == 429:
                return False, "Rate limit"
            elif response.status_code == 403:
                return False, "Bị chặn"
            elif response.status_code == 401:
                return False, "Token hết hạn"
            elif response.status_code == 400:
                return False, f"Bad Request - {response.text[:100]}"
            elif response.status_code == 502:
                return False, "Lỗi server 502"
            else:
                return False, f"Lỗi {response.status_code}"
                
        except Exception as e:
            return False, f"Lỗi kết nối: {e}"

    # ============================================
    # HÀM SPAM
    # ============================================
    def spam_friend_requests(self, count):
        if not self.target_user_id:
            print("[-] Chưa có target. Hãy tìm kiếm trước.")
            return
        
        print(f"\n[+] Bắt đầu spam {count} lời mời đến {self.target_username} (ID: {self.target_user_id})")
        print("[+] Đang gửi...")
        
        success_count = 0
        fail_count = 0
        
        for i in range(1, count + 1):
            delay = random.uniform(1.0, 2.5)
            time.sleep(delay)
            
            success, message = self.send_friend_request(self.target_user_id)
            
            if success:
                success_count += 1
                print(f"  [{i}/{count}] ✓ Gửi thành công")
            else:
                fail_count += 1
                print(f"  [{i}/{count}] ✗ Thất bại: {message}")
            
            if "rate limit" in message.lower():
                print("[!] Rate limit, đợi 10 giây...")
                time.sleep(10)
            if "502" in message:
                print("[!] Lỗi 502, đợi 5 giây...")
                time.sleep(5)
        
        print(f"\n[+] Kết thúc: {success_count} thành công, {fail_count} thất bại")

    # ============================================
    # HÀM CHÍNH
    # ============================================
    def run(self):
        print("=" * 55)
        print("  LOCKET FRIEND SPAM TOOL v6.0")
        print("  (Đã sửa lỗi không hiện lời mời)")
        print("=" * 55)
        
        print("\n[!] LƯU Ý: Bạn cần sửa FRIEND_REQUEST_BODY_TEMPLATE")
        print("[!] theo đúng BODY trong request chuẩn từ Stream.")
        print("[!] Nếu không, lời mời sẽ không hiển thị.")
        print("[!] Xem DEBUG output để kiểm tra.\n")
        
        while True:
            username_input = input("[?] Nhập Username hoặc Link kết bạn: ").strip()
            if username_input:
                if self.search_username(username_input):
                    break
                else:
                    print("[!] Vui lòng nhập lại.")
            else:
                print("[!] Không được bỏ trống.")
        
        while True:
            try:
                count_input = input("[?] Nhập số lượng lời mời (1-30): ").strip()
                count = int(count_input)
                if 1 <= count <= 30:
                    break
                else:
                    print("[!] Vui lòng nhập số từ 1 đến 30.")
            except ValueError:
                print("[!] Vui lòng nhập số hợp lệ.")
        
        print(f"\n[+] Target: {self.target_username} (ID: {self.target_user_id})")
        print(f"[+] Số lượng: {count}")
        confirm = input("[?] Bắt đầu spam? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.spam_friend_requests(count)
        else:
            print("[+] Đã hủy.")

# ============================================
# ĐIỂM VÀO CHƯƠNG TRÌNH
# ============================================
if __name__ == "__main__":
    tool = LocketSpamTool()
    try:
        tool.run()
    except KeyboardInterrupt:
        print("\n[!] Đã dừng bởi người dùng.")
    except Exception as e:
        print(f"[-] Lỗi không mong muốn: {e}")