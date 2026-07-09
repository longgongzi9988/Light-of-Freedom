import requests
import datetime

def fetch_crypto_data():
    # 1. 抓取 BTC 和 ETH 实时价格
    price_url = "https://cryptocompare.com"
    prices = {"BTC": "0.00", "ETH": "0.00"}
    try:
        price_res = requests.get(price_url, timeout=10)
        price_data = price_res.json()
        prices["BTC"] = f"{price_data.get('BTC', {}).get('USD', 0):,}"
        prices["ETH"] = f"{price_data.get('ETH', {}).get('USD', 0):,}"
    except Exception as e:
        print(f"Error fetching prices: {e}")

    # 2. 抓取中文加密货币新闻 (指定 lang=ZH)
    news_url = "https://cryptocompare.com"
    news_list = []
    try:
        news_res = requests.get(news_url, timeout=10)
        news_data = news_res.json()
        articles = news_data.get('Data', [])
        
        for item in articles[:15]:  # 取最新 15 条新闻
            news_list.append({
                'title': item.get('title'),
                'url': item.get('url'),
                'source': item.get('source_info', {}).get('name', '未知来源'),
                'body': item.get('body')[:120] + "..." if item.get('body') else ""
            })
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    return prices, news_list

def generate_html(prices, news_list):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>加密货币世界新闻与行情</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f7fafc; color: #2d3748; }}
        h1 {{ color: #1a365d; text-align: center; margin-bottom: 5px; font-size: 2em; }}
        .update-time {{ text-align: center; color: #718096; font-size: 0.85em; margin-bottom: 25px; }}
        
        /* 价格卡片样式 */
        .price-container {{ display: flex; gap: 15px; margin-bottom: 30px; justify-content: center; }}
        .price-card {{ background: linear-gradient(135deg, #1a365d 0%, #2a4365 100%); color: white; padding: 15px 25px; border-radius: 12px; min-width: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }}
        .price-card.eth {{ background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); }}
        .coin-name {{ font-size: 0.9em; font-weight: bold; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; }}
        .coin-price {{ font-size: 1.6em; font-weight: bold; margin-top: 5px; font-family: 'Courier New', Courier, monospace; }}
        
        /* 新闻卡片样式 */
        .news-card {{ background: white; padding: 22px; margin-bottom: 18px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border-left: 5px solid #3182ce; transition: transform 0.2s; }}
        .news-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        .news-title {{ font-size: 1.25em; font-weight: bold; margin-bottom: 8px; line-height: 1.4; }}
        .news-title a {{ color: #2b6cb0; text-decoration: none; }}
        .news-title a:hover {{ color: #4299e1; text-decoration: underline; }}
        .news-meta {{ font-size: 0.85em; color: #a0aec0; margin-bottom: 12px; display: flex; gap: 10px; }}
        .news-body {{ font-size: 0.95em; color: #4a5568; line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>🪙 加密币世界快讯</h1>
    <div class="update-time">云端自动更新时间 (UTC): {now}</div>
    
    <!-- 实时行情卡片 -->
    <div class="price-container">
        <div class="price-card btc">
            <div class="coin-name">Bitcoin (BTC)</div>
            <div class="coin-price">${prices['BTC']}</div>
        </div>
        <div class="price-card eth">
            <div class="coin-name">Ethereum (ETH)</div>
            <div class="coin-price">${prices['ETH']}</div>
        </div>
    </div>

    <!-- 新闻列表 -->
"""
    
    if not news_list:
        html_content += "<p style='text-align:center; color:#a0aec0;'>暂无中文快讯，正在等待云端下一次抓取...</p>"
    else:
        for news in news_list:
            html_content += f"""
    <div class="news-card">
        <div class="news-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
        <div class="news-meta">
            <span>来源: {news['source']}</span>
        </div>
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
    prices, news = fetch_crypto_data()
    generate_html(prices, news)
    print("网站 2.0 成功生成！")
