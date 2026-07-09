import requests
from bs4 import BeautifulSoup
import datetime

def fetch_crypto_news():
    url = "https://cryptocompare.com"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        articles = data.get('Data', [])
        
        news_list = []
        for item in articles[:15]:
            news_list.append({
                'title': item.get('title'),
                'url': item.get('url'),
                'source': item.get('source_info', {}).get('name', 'Unknown'),
                'body': item.get('body')[:150] + "..."
            })
        return news_list
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def generate_html(news_list):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币世界新闻自动收集</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f6f9; color: #333; }}
        h1 {{ color: #1a365d; text-align: center; }}
        .update-time {{ text-align: center; color: #666; font-size: 0.9em; margin-bottom: 30px; }}
        .news-card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .news-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .news-title a {{ color: #2b6cb0; text-decoration: none; }}
        .news-title a:hover {{ text-decoration: underline; }}
        .news-meta {{ font-size: 0.85em; color: #718096; margin-bottom: 10px; }}
        .news-body {{ font-size: 0.95em; color: #4a5568; line-height: 1.5; }}
    </style>
</head>
<body>
    <h1>🪙 加密世界新闻</h1>
    <div class="update-time">最后更新时间 (UTC): {now}</div>
"""
    
    if not news_list:
        html_content += "<p style='text-align:center;'>暂无新闻，请稍后再试。</p>"
    else:
        for news in news_list:
            html_content += f"""
    <div class="news-card">
        <div class="news-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
        <div class="news-meta">来源: {news['source']}</div>
        <div class="news-body">{news['body']}</div>
    </div>
"""
            
    html_content += """
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    news = fetch_crypto_news()
    generate_html(news)
    print("HTML generated successfully!")
