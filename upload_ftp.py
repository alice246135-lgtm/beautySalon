import ftplib
import os
import time

HOST = "ftp.byethost7.com"
USER = "b7_41743928"
PASS = "ccy153"
REMOTE_BASE = "/htdocs"
LOCAL_BASE = "/Users/taialisia/Desktop/碩一下/搜索引擎/perfectcut-1.0.0"

SKIP = {".vscode", "upload_ftp.py", "Web_Trial_zh-Hant.exe", "js copy", ".DS_Store", "README.md"}

def ensure_remote_dir(ftp, path):
    parts = path.split("/")
    current = ""
    for part in parts:
        if not part:
            continue
        current += "/" + part
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass

def upload_file_with_retry(ftp, local_path, remote_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"  ✅ 上傳: {remote_path}")
            return True
        except Exception as e:
            print(f"  ⚠️ 上傳失敗 {remote_path} (嘗試 {attempt+1}/{max_retries}): {e}")
            time.sleep(2)
            try:
                # 重新連線
                ftp.connect(HOST, 21, timeout=60)
                ftp.login(USER, PASS)
                ftp.set_pasv(True)
            except:
                pass
    print(f"  ❌ 放棄上傳: {remote_path}")
    return False

def upload_dir(ftp, local_dir, remote_dir):
    ensure_remote_dir(ftp, remote_dir)
    for item in os.listdir(local_dir):
        if item in SKIP or item.startswith("."):
            continue
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item
        if os.path.isdir(local_path):
            upload_dir(ftp, local_path, remote_path)
        else:
            upload_file_with_retry(ftp, local_path, remote_path)

for attempt in range(5):
    print(f"🔌 連線到 FTP 伺服器... (嘗試 {attempt+1}/5)")
    try:
        ftp = ftplib.FTP()
        ftp.connect(HOST, 21, timeout=60)
        ftp.login(USER, PASS)
        ftp.set_pasv(True)
        print(f"✅ 登入成功！帳號: {USER}")
        print("\n📤 開始上傳檔案...\n")
        upload_dir(ftp, LOCAL_BASE, REMOTE_BASE)
        ftp.quit()
        print("\n🎉 上傳完成！")
        break
    except Exception as e:
        print(f"連線或上傳發生錯誤: {e}")
        time.sleep(5)
