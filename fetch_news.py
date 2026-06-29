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
    # 注入金十数据严格校验的特定App-Id和版本请求头，彻底阻断502/空数据
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.jin10.com/",
        "x-app-id": "SO1EJGmNgCtmpcPF",
        "x-version": "1.0.0"
    }
    # 使用包含渠道参数和动态时间戳的官方实时API
    url = f"https://jin10.com{int(time.time() * 1000)}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"请求金十失败，HTTP状态码: {response.status_code}")
            return []
        
        data = response.json()
        raw_news = data.get("data", [])
        
        if not raw_news:
            print("警告：金十接口返回的数据列表为空！")
            return []
            
        news_list = []
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for item in raw_news:
            # 兼容处理：获取内容主体
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
                
                # 基于快讯内容计算特征哈希，从根本上解决重复问题
                news_id = hashlib.md5(clean_content.encode("utf-8")).hexdigest()
                
                full_time = item.get("time", "")
                time_part = full_time.split(" ")[1] if " " in full_time else full_time
                
                news_list.append({
                    "id": news_id,
                    "date": current_date,
                    "time": time_part[:8],  # 格式化时分秒
                    "content": clean_content
                })
        return news_list
    except Exception as e:
        print(f"抓取金十数据时发生异常: {e}")
        return []

def generate_news_card_html(news):
    """完美映射你的高质感暗黑科技风 article 结构"""
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
        print("未获取到第一手新资讯，本次全自动流程提前中止。")
        return

    if not os.path.exists(HTML_FILE_PATH):
        print(f"未找到对应的HTML网页文件: {HTML_FILE_PATH}")
        return
        
    with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    start_tag = "<!-- AUTOMATIC_POSTS_START -->"
    end_tag = "<!-- AUTOMATIC_POSTS_END -->"
    
    if start_tag not in html_content or end_tag not in html_content:
        print("错误：index.html 中未检测到定位注释标签！")
        return

    # 使用 BeautifulSoup 精准解析页面中现有的旧卡片，确保提取完全
    soup = BeautifulSoup(html_content, "html.parser")
    existing_cards = soup.find_all("article", class_="card")
    existing_ids = [card.get("data-id") for card in existing_cards if card.get("data-id")]

    # 循环过滤并压入全新卡片
    new_cards_html = []
    new_added_count = 0
    for news in reversed(latest_news):
        if news["id"] not in existing_ids:
            new_cards_html.append(generate_news_card_html(news))
            new_added_count += 1

    # 兜底机制：如果是完全空白的网页，强行灌入初始最新数据
    if new_added_count == 0 and len(existing_cards) > 0:
        print("没有检测到更新的内容，无需修改网页。")
        return

    print(f"检测到 {new_added_count} 条全量最新快讯，正在合并写入...")

    # 提取过滤旧卡片
    old_cards_str = [str(card) for card in existing_cards if card.get("data-id")]
    
    # 合并、裁切
    all_cards = new_cards_html + old_cards_str
    all_cards = all_cards[:MAX_NEWS_COUNT]

    # 【健壮的定位替换算法】解决定位标记中间完全留白引发的拼接死锁
    start_idx = html_content.find(start_tag) + len(start_tag)
    end_idx = html_content.find(end_tag)
    
    updated_section = "\n" + "\n".join(all_cards) + "\n        "
    new_html = html_content[:start_idx] + updated_section + html_content[end_idx:]

    with open(HTML_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("恭喜！网页数据重写合并成功！")

if __name__ == "__main__":
    update_html_page()
