name: Auto Fetch Jin10 News

on:
  schedule:
    # 每 15 分钟自动运行一次
    - cron: '*/15 * * * *'
  workflow_dispatch: # 允许手动点击按钮触发更新

# 显式允许机器人修改仓库代码
permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4

    - name: Run update script
      run: python fetch_news.py

    - name: Commit and Push changes
      run: |
        git config --global user.name "github-actions[bot]"
        git config --global user.email "41898282+github-actions[bot]@://github.com"
        git add index.html
        # 核心修复：这里修改成了 origin master，完美对齐你的仓库主分支
        git diff-index --quiet HEAD || (git commit -m "🤖 自动同步最新金十快讯" && git push origin master)
