#!/bin/bash

# 查看仓库2023-2025提交用户信息
git log --since="2023-01-01" --until="2025-12-31" --pretty=format:"%an <%ae>" | sort | uniq 

# 配置要修改的信息，匹配旧的邮箱全都换成新的用户和邮箱
OLD_EMAIL="109193776+xxxx@users.noreply.github.com"
NEW_NAME="xxxxx"
NEW_EMAIL="xxxx@gmail.com"

# 检查 git-filter-repo 是否安装
if ! command -v git-filter-repo &> /dev/null; then
    echo "git-filter-repo 未安装，尝试安装..."
    pip install git-filter-repo || { echo "安装失败，请手动安装"; exit 1; }
fi

# 提示确认
echo "⚠️ 你即将重写历史，所有提交 SHA 会改变！请确保已备份仓库。"
read -p "确认继续？(yes/NO) " confirm
if [ "$confirm" != "yes" ]; then
    echo "操作已取消"
    exit 0
fi

# 只修改所有分支
#git filter-repo --force --commit-callback

# 执行修改main分支
git filter-repo --force --refs refs/heads/main --commit-callback '
if commit.author_email == b"'"$OLD_EMAIL"'" :
    commit.author_name = b"'"$NEW_NAME"'"
    commit.author_email = b"'"$NEW_EMAIL"'"
if commit.committer_email == b"'"$OLD_EMAIL"'" :
    commit.committer_name = b"'"$NEW_NAME"'"
    commit.committer_email = b"'"$NEW_EMAIL"'"
'

echo "✅ 历史提交用户名和邮箱已修改完成！"

echo "提示："
echo "有时需要重新添加远程仓库地址： git remote add origin https://github.com/xxx/xxx.git"
echo "可遍历校验仓库文件md5值：     find . -type f ! -path \"./.git/*\" -exec md5sum {} \; "
echo "推送到远程仓库（会重写历史）： git push --force --tags origin 'refs/heads/*'"
