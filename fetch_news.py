import requests
import xml.etree.ElementTree as ET
import datetime

def fetch_crypto_data():
    prices = {"BTC": "0.00", "ETH": "0.00"}
    
    # 1. 修复价格抓取：切换到 CoinGecko 无需 API 密钥的公开端点
    try:
        price_url = "https://coingecko.com"
        # 增加 Headers 防止被服务器拒绝
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        price_res = requests.get(price_url, headers=headers, timeout=10)
        if price_res.status_code == 200:
            price_data = price_res.json()
            btc_price = price_data.get('bitcoin', {}).get('usd', 0)
            eth_price = price_data.get('ethereum', {}).get('usd', 0)
            prices["BTC"] = f"{btc_price:,}" if btc_price else "0.00"
            prices["ETH"] = f"{eth_price:,}" if eth_price else "0.00"
    except Exception as e:
        print(f"Error fetching prices: {e}")

    # 2. 修复中文新闻：使用最稳定的星球日报/巴比特 RSS 中文加密币实时源
    news_list = []
    try:
        # 使用专门的公开中文加密币快讯 RSS
        news_url = "https://rsshub.app"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        news_res = requests.get(news_url, headers=headers, timeout=12)
        
        if news_res.status_code == 200:
            root = ET.fromstring(news_res.content)
            # 解析标准的 RSS XML 格式
            items = root.findall('.//item')
            for item in items[:15]:  # 获取最新 15 条
                title = item.find('title').text if item.find('title') is not None else "加密币快讯"
                url = item.find('link').text if item.find('link') is not None else "#"
                description = item.find('description').text if item.find('description') is not None else ""
                
                # 简单清洗 HTML 标签以提取纯文本简介
                import re
                clean_body = re.sub(r'<[^>]+>', '', description)[:150] + "..."
                
                news_list.append({
                    'title': title,
                    'url': url,
                    'source': "Odaily 星球日报",
                    'body': clean_body
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
        
        /* 行情样式 */
        .price-container {{ display: flex; gap: 15px; margin-bottom: 30px; justify-content: center; }}
        .price-card {{ background: linear-gradient(135deg, #1a365d 0%, #2a4365 100%); color: white; padding: 15px 25px; border-radius: 12px; min-width: 160px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }}
        .price-card.eth {{ background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%); }}
        .coin-name {{ font-size: 0.9em; font-weight: bold; opacity: 0.8; text-transform: uppercase; letter-spacing: 1px; }}
        .coin-price {{ font-size: 1.6em; font-weight: bold; margin-top: 5px; font-family: 'Courier New', Courier, monospace; }}
        
        /* 新闻样式 */
        .news-card {{ background: white; padding: 22px; margin-bottom: 18px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border-left: 5px solid #3182ce; transition: transform 0.2s; }}
        .news-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
        .news-title {{ font-size: 1.25em; font-weight: bold; margin-bottom: 8px; line-height: 1.4; }}
        .news-title a {{ color: #2b6cb0; text-decoration: none; }}
        .news-title a:hover {{ color: #4299e1; text-decoration: underline; }}
        .news-meta {{ font-size: 0.85em; color: #a0aec0; margin-bottom: 12px; }}
        .news-body {{ font-size: 0.95em; color: #4a5568; line-height: 1.6; }}
    </style>
</head>
<body>
    <h1>🪙 加密币世界快讯</h1>
    <div class="update-time">云端自动更新时间 (UTC): {now}</div>
    
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
"""
    
    if not news_list:
        html_content += "<p style='text-align:center; color:#a0aec0;'>暂无新快讯，请稍后刷新重试...</p>"
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
    prices, news = fetch_crypto_data()
    generate_html(prices, news)
    print("修复版网站成功生成！")
