import os
import hashlib
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 配置项
HTML_FILE_PATH = "index.html"  # 你的HTML文件路径
MAX_NEWS_COUNT = 10           # 页面最多保留的新闻条数

def get_jin10_flash_news():
    """从金十数据接口抓取最新的快讯"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://jin10.com"
    }
    url = f"https://jin10.com{int(time.time() * 1000)}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return []
        
        data = response.json()
        raw_news = data.get("data", [])
        
        news_list = []
        # 获取今天的日期，格式如 2026-06-29
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for item in raw_news:
            if item.get("type") == 0:  # 纯文字快讯
                soup = BeautifulSoup(item.get("data", {}).get("content", ""), "html.parser")
                clean_content = soup.get_text().strip()
                
                if not clean_content:
                    continue
                
                # 生成唯一特征标识（MD5），写入 data-id 用于绝对去重
                news_id = hashlib.md5(clean_content.encode("utf-8")).hexdigest()
                
                # 提取快讯的具体具体时分秒
                full_time = item.get("time", "")
                time_part = full_time.split(" ")[1] if " " in full_time else full_time
                
                news_list.append({
                    "id": news_id,
                    "date": current_date,
                    "time": time_part,
                    "content": clean_content
                })
        return news_list
    except Exception as e:
        print(f"抓取金十数据出错: {e}")
        return []

def generate_news_card_html(news):
    """完美对齐你的暗黑科技风 HTML 结构"""
    return f"""        <article class="card" data-id="{news['id']}">
            <div class="meta">
                <span class="date">{news['date']} {news['time']}</span>
                <span class="tag">Jin10 Flash</span>
            </div>
            <h2 class="title">金十财经实时快讯追踪</h2>
            <div class="content">
                <p>{news['content']}</p>
                <p>💡 <em>Brief: 自动化系统实时追踪，防重复特征已锁定。</em></p>
            </div>
        </article>"""

def update_html_page():
    latest_news = get_jin10_flash_news()
    if not latest_news:
        print("未获取到有效新闻，取消更新。")
        return

    if not os.path.exists(HTML_FILE_PATH):
        print(f"未找到目标文件 {HTML_FILE_PATH}")
        return
        
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    start_tag = "<!-- AUTOMATIC_POSTS_START -->"
    end_tag = "<!-- AUTOMATIC_POSTS_END -->"
    
    if start_tag not in html_content or end_tag not in html_content:
        print("错误：HTML 中未找到定位注释标签！")
        return

    # 完美对齐：从你的现有页面提取所有的 article.card 的 data-id
    soup = BeautifulSoup(html_content, "html.parser")
    existing_ids = [card.get("data-id") for card in soup.find_all("article", class_="card") if card.get("data-id")]

    # 过滤重复新闻
    new_cards_html = []
    new_added_count = 0
    for news in reversed(latest_news):
        if news["id"] not in existing_ids:
            new_cards_html.append(generate_news_card_html(news))
            new_added_count += 1

    if new_added_count == 0:
        print("没有检测到新发布的新闻，无需更新网页。")
        return

    print(f"检测到 {new_added_count} 条全新的金十快讯，正在写入...")

    # 切割并提取现有的老卡片
    parts_start = html_content.split(start_tag)
    before_news = parts_start[0]
    rest = parts_start[1]
    
    parts_end = rest.split(end_tag)
    news_section = parts_end[0]
    after_news = parts_end[1]
    
    old_soup = BeautifulSoup(news_section, "html.parser")
    # 提取旧卡片
    old_cards = []
    for card in old_soup.find_all("article", class_="card"):
        old_cards.append(str(card))
    
    # 崭新快讯塞在最上面 + 合并旧卡片，严格裁剪数量
    all_cards = new_cards_html + old_cards
    all_cards = all_cards[:MAX_NEWS_COUNT]

    # 重新拼装写回
    updated_section = "\n" + "\n".join(all_cards) + "\n        "
    new_html = f"{before_news}{start_tag}{updated_section}{end_tag}{after_news}"

    with open(HTML_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("网页更新成功！")

if __name__ == "__main__":
    update_html_page()
