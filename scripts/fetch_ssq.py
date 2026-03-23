#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球历史开奖数据爬取脚本
数据来源：中国福彩网 (zhcw.com)
"""

import requests
import re
import time
from datetime import datetime

def fetch_page(page_num):
    """获取指定页码的开奖数据"""
    url = f"https://kaijiang.zhcw.com/zhcw/html/ssq/list_{page_num}.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取第{page_num}页失败：{e}")
        return None

def parse_lottery_data(html):
    """解析 HTML 提取开奖数据"""
    results = []
    
    # 匹配开奖记录行
    pattern = r'<tr>\s*<td align="center">([^<]+)</td>\s*<td align="center">([^<]+)</td>\s*<td align="center" style="padding-left:10px;">(.*?)</td>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for match in matches:
        date = match[0].strip()
        issue = match[1].strip()
        numbers_html = match[2]
        
        # 提取红球和蓝球
        red_balls = re.findall(r'<em class="rr">(\d+)</em>', numbers_html)
        blue_balls = re.findall(r'<em>(\d+)</em>', numbers_html)
        
        if red_balls and blue_balls:
            red_str = ' '.join(red_balls)
            blue_str = blue_balls[0] if blue_balls else ''
            results.append({
                'date': date,
                'issue': issue,
                'red': red_str,
                'blue': blue_str
            })
    
    return results

def main():
    all_results = []
    
    # 双色球大约每页 20 条记录，10 年约 1500+ 期，需要爬取约 75 页
    # 从 2016 年到 2026 年
    print("开始爬取双色球历史开奖数据...")
    print(f"起始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for page in range(1, 100):  # 最多爬取 100 页
        print(f"正在获取第 {page} 页...")
        html = fetch_page(page)
        
        if not html:
            print(f"第 {page} 页获取失败，跳过")
            continue
        
        results = parse_lottery_data(html)
        
        if not results:
            print(f"第 {page} 页没有数据，可能已到达最早记录")
            break
        
        all_results.extend(results)
        print(f"  获取到 {len(results)} 条记录，累计 {len(all_results)} 条")
        
        # 检查是否到达最后一页（数据量不足 20 条）
        if len(results) < 20:
            print("已到达最后一页")
            break
        
        # 礼貌性延迟
        time.sleep(0.5)
    
    # 保存数据
    output_file = "/home/dancekey/.openclaw/workspace/data/ssq_history.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("双色球历史开奖记录\n")
        f.write(f"数据更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"共 {len(all_results)} 期开奖数据\n")
        f.write("=" * 60 + "\n\n")
        f.write("格式：开奖日期 | 期号 | 红球 (6 个) | 蓝球 (1 个)\n")
        f.write("-" * 60 + "\n\n")
        
        for item in all_results:
            f.write(f"{item['date']} | {item['issue']} | 红球：{item['red']} | 蓝球：{item['blue']}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("数据来源：中国福彩网 (https://www.zhcw.com)\n")
        f.write("注：红球范围 1-33，蓝球范围 1-16\n")
    
    print(f"\n数据已保存到：{output_file}")
    print(f"共保存 {len(all_results)} 期开奖记录")

if __name__ == "__main__":
    main()
