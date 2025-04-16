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
print(f"已加载 TOKEN: {TOKEN[:6]}... (长度: {len(TOKEN) if TOKEN else 0})")

if not TOKEN:
    print("❌ GitHub Token 未设置在环境变量中。")

# 设置 GitHub 相关信息
REPO_OWNER = "nihil7"  # 仓库所有者
REPO_NAME = "PtSignnA"  # 仓库名称
FILE_PATH = ".github/workflows/RunDaily.yml"  # 目标文件路径


# 生成随机的 cron 时间
def generate_random_cron():
    minute = random.randint(0, 59)  # 修改为任意分钟
    cron = f"{minute} 22 * * *"
    print(f"📅 生成的随机 cron (UTC): {cron} | 北京时间约为次日 {6 + minute // 60}:{minute % 60:02d}")
    return cron


# 获取文件的当前内容（Base64 编码）和 SHA
def get_file_info():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}

    print(f"📥 正在获取文件: {url}")
    response = requests.get(url, headers=headers)

    print(f"📡 GET 状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ 获取文件信息时出错: {response.text}")
        return None, None

    file_data = response.json()
    return file_data["content"], file_data["sha"]


# 更新文件内容
def update_file(file_content, sha):
    new_cron = generate_random_cron()

    try:
        decoded_content = base64.b64decode(file_content).decode('utf-8')
    except Exception as e:
        print(f"❌ 解码 Base64 内容时出错: {e}")
        return

    print("📄 当前文件内容（开始部分）:")
    print(decoded_content[:300])

    # 替换 cron 字段
    updated_content = re.sub(r"cron: '\d{1,2} 22 \* \* \*'", f"cron: '{new_cron}'", decoded_content)

    if decoded_content == updated_content:
        print("⚠️ 内容没有变化。请检查原始的 cron 格式是否匹配。")
    else:
        print("✅ 更新后的内容预览:")
        print(updated_content[:300])

    # 编码为 Base64
    encoded_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

    # API 请求体
    data = {
        "message": f"更新 cron 为 {new_cron}",
        "content": encoded_content,
        "sha": sha
    }

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    print(f"📤 发送 PUT 请求到: {url}")
    response = requests.put(url, headers={"Authorization": f"token {TOKEN}"}, json=data)

    print(f"📡 PUT 状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ 成功将 cron 更新为 {new_cron}")
    else:
        print(f"❌ 更新文件时出错: {response.text}")


# 主流程
def main():
    if not TOKEN:
        print("❌ Token 未设置，终止程序。")
        return

    file_content, sha = get_file_info()
    if file_content and sha:
        update_file(file_content, sha)
    else:
        print("❌ 获取文件内容或 sha 时失败，终止程序。")


if __name__ == "__main__":
    main()
