import random
import datetime
import re
import os
from pathlib import Path

TARGET_REPO_PATH = "./auto-checkin"
WORKFLOW_FILE = Path(TARGET_REPO_PATH) / ".github/workflows/auto_checkin.yml"

def generate_random_cron():
    # 生成 6:00 到 6:59 之间的随机时间（UTC 即 22:00 ~ 22:59）
    minute = random.randint(0, 59)
    return f"{minute} 22 * * *"

def replace_cron_line(content, new_cron):
    return re.sub(r"cron: '.*?'", f"cron: '{new_cron}'", content)

def main():
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    new_cron = generate_random_cron()
    updated = replace_cron_line(content, new_cron)

    with open(WORKFLOW_FILE, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(f"Updated cron to: {new_cron}")

    os.chdir(TARGET_REPO_PATH)
    os.system("git config user.name 'github-actions'")
    os.system("git config user.email 'github-actions@github.com'")
    os.system("git add .github/workflows/auto_checkin.yml")
    os.system(f"git commit -m 'Update cron to {new_cron}' || echo 'No changes to commit'")
    os.system("git push")

if __name__ == "__main__":
    main()
