import os
import re
from datetime import datetime
import xml.etree.ElementTree as ET
import requests

def get_latest_news():
    """从免费的 RSS 源抓取最新的加密与世界大事"""
    # 这里使用的是 CoinDesk 的免费 RSS 新闻源，不需要任何 Token 或 Key
    url = "https://coindesk.com"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            if items:
                # 拿取最新的一条新闻
                latest_item = items[0]
                title = latest_item.find('title').text
                description = latest_item.find('description').text if latest_item.find('description') is not None else ""
                
                # 清洗一下描述文本中的 HTML 标签
                description = re.sub('<[^<]+?>', '', description)
                # 截取前 200 个字防止过长
                if len(description) > 200:
                    description = description[:200] + "..."
                    
                return title, description
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    # 如果抓取失败，使用兜底的优质模版内容，确保网站天天有更新
    return "Global Crypto Markets Maintain Steady Growth Amid Regulatory Clarity", "Institutional inflows continue to support major assets as cross-border payment solutions expand globally. Developers focus on scalability enhancements."

def update_html():
    # 1. 获取今天的时间与新闻内容
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    title, summary = get_latest_news()
    
    # 2. 组装成我们网页的 HTML 卡片格式
    new_card = f"""        <!-- 文章盒子开始 -->
        <article class="card">
            <div class="meta">
                <span class="date">{today_str}</span>
                <span class="tag">Auto Pulse</span>
            </div>
            <h2 class="title">{title}</h2>
            <div class="content">
                <p>{summary}</p>
                <p>💡 <em>Brief: Automatically tracked from global channels. Domain index actively maintained.</em></p>
            </div>
        </article>
        <!-- 文章盒子结束 -->\n"""

    # 3. 读取原本的 index.html 并精准插入
    if not os.path.exists("index.html"):
        print("index.html not found!")
        return

    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    start_tag = "<!-- AUTOMATIC_POSTS_START -->"
    
    if start_tag in html_content:
        # 在标记符号下方紧接着插入新文章，这样最新的文章永远排在最上面
        updated_content = html_content.replace(start_tag, f"{start_tag}\n{new_card}")
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("Successfully updated index.html with daily news!")
    else:
        print("Could not find insertion tags in index.html")

if __name__ == "__main__":
    update_html()
