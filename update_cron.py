import os
import requests
import base64
import random
from dotenv import load_dotenv
import re

# 加载 .env 文件
load_dotenv()

# 获取 TOKEN 环境变量
TOKEN = os.getenv('TOKEN')
print(f"Loaded TOKEN: {TOKEN[:6]}... (Length: {len(TOKEN) if TOKEN else 0})")

if not TOKEN:
    print("❌ GitHub Token is not set in the environment variables.")

# 设置 GitHub 相关信息
REPO_OWNER = "nihil7"  # 仓库所有者
REPO_NAME = "PtSignnA"  # 仓库名称
FILE_PATH = ".github/workflows/RunDaily.yml"  # 目标文件路径


# 生成随机的 cron 时间
def generate_random_cron():
    minute = random.randint(0, 59)  # 修改为任意分钟
    cron = f"{minute} 22 * * *"
    print(f"📅 Generated random cron (UTC): {cron} | 北京时间约为次日 {6 + minute // 60}:{minute % 60:02d}")
    return cron


# 获取文件的当前内容（Base64 编码）和 SHA
def get_file_info():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}

    print(f"📥 Fetching file from: {url}")
    response = requests.get(url, headers=headers)

    print(f"📡 GET Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ Error fetching file info: {response.text}")
        return None, None

    file_data = response.json()
    return file_data["content"], file_data["sha"]


# 更新文件内容
def update_file(file_content, sha):
    new_cron = generate_random_cron()

    try:
        decoded_content = base64.b64decode(file_content).decode('utf-8')
    except Exception as e:
        print(f"❌ Error decoding Base64 content: {e}")
        return

    print("📄 Current file content (start):")
    print(decoded_content[:300])

    # 替换 cron 字段
    updated_content = re.sub(r"cron: '\d{1,2} 22 \* \* \*'", f"cron: '{new_cron}'", decoded_content)

    if decoded_content == updated_content:
        print("⚠️ No change in content. Check if the original cron format is matched.")
    else:
        print("✅ Updated content preview:")
        print(updated_content[:300])

    # 编码为 Base64
    encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

    # API 请求体
    data = {
        "message": f"Update cron to {new_cron}",
        "content": encoded_content,
        "sha": sha
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    print(f"📤 Sending PUT request to: {url}")
    response = requests.put(url, headers={"Authorization": f"token {TOKEN}"}, json=data)

    print(f"📡 PUT Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Successfully updated cron to {new_cron}")
    else:
        print(f"❌ Error updating file: {response.text}")


# 主流程
def main():
    if not TOKEN:
        print("❌ GitHub Token is not set. Aborting.")
        return

    file_content, sha = get_file_info()
    if file_content and sha:
        update_file(file_content, sha)
    else:
        print("❌ Failed to retrieve file content or sha. Aborting.")


if __name__ == "__main__":
    main()
