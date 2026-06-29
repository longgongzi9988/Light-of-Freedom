import os
import hashlib
import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

HTML_FILE_PATH = "index.html"  
MAX_NEWS_COUNT = 10           

def get_jin10_flash_news():
    """从金十数据接口抓取最新的快讯"""
    print("====== 1. 开始请求金十数据接口 ======")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://jin10.com",
        "x-app-id": "SO1EJGmNgCtmpcPF",
        "x-version": "1.0.0"
    }
    url = f"https://jin10.com{int(time.time() * 1000)}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"[日志] HTTP 状态码: {response.status_code}")
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        raw_news = data.get("data", [])
        print(f"[日志] 成功获取到原始数据条数: {len(raw_news)}")
        
        news_list = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for item in raw_news:
            content_block = item.get("data", {})
            if isinstance(content_block, dict):
                content_text = content_block.get("content", "")
            else:
                continue
                
            if content_text:
                soup = BeautifulSoup(content_text, "html.parser")
                clean_content = soup.get_text().strip()
                
                if not clean_content:
                    continue
                
                news_id = hashlib.md5(clean_content.encode("utf-8")).hexdigest()
                full_time = item.get("time", "")
                time_part = full_time.split(" ") if " " in full_time else [full_time]
                actual_time = time_part[-1][:8]
                
                news_list.append({
                    "id": news_id,
                    "date": current_date,
                    "time": actual_time,
                    "content": clean_content
                })
        print(f"[日志] 过滤解析出有效纯文本快讯条数: {len(news_list)}")
        return news_list
    except Exception as e:
        print(f"[错误] 抓取网络数据时发生异常: {e}")
        return []

def generate_news_card_html(news):
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
        print("[中断] 未能获取到任何金十新闻内容，脚本提前退出。")
        # 强制抛出异常以便在 GitHub 上显示红叉日志，帮我们排查是不是金十封了IP
        raise Exception("无法获取新闻数据，可能是由于网络被金十拦截")

    print("====== 2. 开始检查本地 HTML 文件 ======")
    if not os.path.exists(HTML_FILE_PATH):
        print(f"[错误] 在根目录下没有找到对应的网页文件: {HTML_FILE_PATH}")
        raise FileNotFoundError(f"找不到 {HTML_FILE_PATH}")
        
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    start_tag = "<!-- AUTOMATIC_POSTS_START -->"
    end_tag = "<!-- AUTOMATIC_POSTS_END -->"
    
    if start_tag not in html_content or end_tag not in html_content:
        print("[错误] index.html 中未检测到关键的定位注释标签！")
        print(f"请检查 index.html 中是否包含：{start_tag} 和 {end_tag}")
        raise ValueError("HTML文件缺少定位注释标签")

    soup = BeautifulSoup(html_content, "html.parser")
    existing_cards = soup.find_all("article", class_="card")
    existing_ids = [card.get("data-id") for card in existing_cards if card.get("data-id")]
    print(f"[日志] 当前网页上已存在的卡片数量: {len(existing_cards)}，去重ID数量: {len(existing_ids)}")

    new_cards_html = []
    new_added_count = 0
    for news in reversed(latest_news):
        if news["id"] not in existing_ids:
            new_cards_html.append(generate_news_card_html(news))
            new_added_count += 1

    print(f"[日志] 本次对比发现了 {new_added_count} 条全量最新快讯")

    old_cards_str = [str(card) for card in existing_cards if card.get("data-id")]
    all_cards = new_cards_html + old_cards_str
    all_cards = all_cards[:MAX_NEWS_COUNT]

    print("====== 3. 开始执行 HTML 文件重写 ======")
    start_idx = html_content.find(start_tag) + len(start_tag)
    end_idx = html_content.find(end_tag)
    
    updated_section = "\n" + "\n".join(all_cards) + "\n        "
    new_html = html_content[:start_idx] + updated_section + html_content[end_idx:]

    with open(HTML_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("[成功] 恭喜！网页数据重写合并成功！")

if __name__ == "__main__":
    update_html_page()
