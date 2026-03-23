#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球数据分析脚本
涵盖 8 大分析方向，生成 markdown 报告
"""

import re
from datetime import datetime
from collections import Counter, defaultdict

def load_data(filepath):
    """加载开奖数据"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' in line and '红球：' in line and '蓝球：' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    date = parts[0].strip()
                    issue = parts[1].strip()
                    red_part = parts[2].strip()
                    blue_part = parts[3].strip()
                    
                    # 提取红球号码（去掉"红球："前缀）
                    red_str = red_part.replace('红球：', '').strip()
                    # 提取蓝球号码（去掉"蓝球："前缀）
                    blue_str = blue_part.replace('蓝球：', '').strip()
                    
                    # 只保留数字
                    red_balls = [int(x) for x in red_str.split() if x.isdigit()]
                    blue_ball = int(blue_str) if blue_str.isdigit() else 0
                    
                    if len(red_balls) == 6 and blue_ball > 0:
                        data.append({
                            'date': date,
                            'issue': issue,
                            'red': red_balls,
                            'blue': blue_ball
                        })
    return data

def analyze_hot_cold(data):
    """1. 热号冷号统计"""
    red_counter = Counter()
    blue_counter = Counter()
    
    for item in data:
        for ball in item['red']:
            red_counter[ball] += 1
        blue_counter[item['blue']] += 1
    
    # 红球热号 TOP10
    red_hot = red_counter.most_common(10)
    red_cold = red_counter.most_common()[:-11:-1]
    
    # 蓝球热号 TOP5
    blue_hot = blue_counter.most_common(5)
    blue_cold = blue_counter.most_common()[:-6:-1]
    
    return {
        'red_hot': red_hot,
        'red_cold': red_cold,
        'blue_hot': blue_hot,
        'blue_cold': blue_cold,
        'red_total': red_counter,
        'blue_total': blue_counter
    }

def analyze_omission(data):
    """2. 遗漏值分析"""
    # 计算每个号码当前遗漏期数
    red_omission = {i: 0 for i in range(1, 34)}
    blue_omission = {i: 0 for i in range(1, 17)}
    
    # 从最新一期往前遍历
    for item in reversed(data):
        for ball in item['red']:
            red_omission[ball] = 0
        red_omission[item['blue']] = 0
        
        # 其他号码遗漏 +1
        for i in range(1, 34):
            if i not in item['red']:
                red_omission[i] += 1
        for i in range(1, 17):
            if i != item['blue']:
                blue_omission[i] += 1
        break  # 只需要最新一期
    
    # 计算历史最大遗漏
    red_max_omission = {i: 0 for i in range(1, 34)}
    blue_max_omission = {i: 0 for i in range(1, 17)}
    
    current_red_omission = {i: 0 for i in range(1, 34)}
    current_blue_omission = {i: 0 for i in range(1, 17)}
    
    for item in data:
        for i in range(1, 34):
            if i in item['red']:
                current_red_omission[i] = 0
            else:
                current_red_omission[i] += 1
                red_max_omission[i] = max(red_max_omission[i], current_red_omission[i])
        
        for i in range(1, 17):
            if i == item['blue']:
                current_blue_omission[i] = 0
            else:
                current_blue_omission[i] += 1
                blue_max_omission[i] = max(blue_max_omission[i], current_blue_omission[i])
    
    return {
        'current_red': red_omission,
        'current_blue': blue_omission,
        'max_red': red_max_omission,
        'max_blue': blue_max_omission
    }

def analyze_odd_even_big_small(data):
    """3. 奇偶/大小比例分析"""
    odd_even_dist = Counter()
    big_small_dist = Counter()
    
    for item in data:
        odd_count = sum(1 for x in item['red'] if x % 2 == 1)
        even_count = 6 - odd_count
        odd_even_dist[f"{odd_count}奇{even_count}偶"] += 1
        
        big_count = sum(1 for x in item['red'] if x >= 17)
        small_count = 6 - big_count
        big_small_dist[f"{big_count}大{small_count}小"] += 1
    
    return {
        'odd_even': odd_even_dist.most_common(),
        'big_small': big_small_dist.most_common()
    }

def analyze_sum(data):
    """4. 和值走势分析"""
    sums = [sum(item['red']) for item in data]
    
    return {
        'min': min(sums),
        'max': max(sums),
        'avg': sum(sums) / len(sums),
        'recent_10': sums[-10:],
        'distribution': Counter(sums).most_common(10)
    }

def analyze_consecutive(data):
    """5. 连号分析"""
    two_consecutive = 0
    three_consecutive = 0
    four_plus_consecutive = 0
    
    for item in data:
        red_sorted = sorted(item['red'])
        consecutive_count = 1
        max_consecutive = 1
        
        for i in range(1, len(red_sorted)):
            if red_sorted[i] == red_sorted[i-1] + 1:
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 1
        
        if max_consecutive >= 4:
            four_plus_consecutive += 1
        elif max_consecutive == 3:
            three_consecutive += 1
        elif max_consecutive == 2:
            two_consecutive += 1
    
    total = len(data)
    return {
        'two': two_consecutive,
        'three': three_consecutive,
        'four_plus': four_plus_consecutive,
        'none': total - two_consecutive - three_consecutive - four_plus_consecutive,
        'total': total
    }

def analyze_blue(data):
    """6. 蓝球专项分析"""
    blue_counter = Counter(item['blue'] for item in data)
    
    # 奇偶
    odd = sum(1 for item in data if item['blue'] % 2 == 1)
    even = len(data) - odd
    
    # 大小 (1-8 小，9-16 大)
    small = sum(1 for item in data if item['blue'] <= 8)
    big = len(data) - small
    
    # 012 路
    road = Counter(item['blue'] % 3 for item in data)
    
    return {
        'distribution': blue_counter.most_common(),
        'odd': odd,
        'even': even,
        'big': big,
        'small': small,
        'road0': road[0],
        'road1': road[1],
        'road2': road[2]
    }

def analyze_zones(data):
    """7. 区间分布分析"""
    # 三区：1-11, 12-22, 23-33
    zone_dist = Counter()
    
    for item in data:
        zone1 = sum(1 for x in item['red'] if 1 <= x <= 11)
        zone2 = sum(1 for x in item['red'] if 12 <= x <= 22)
        zone3 = sum(1 for x in item['red'] if 23 <= x <= 33)
        zone_dist[f"{zone1}-{zone2}-{zone3}"] += 1
    
    # 五区：1-7, 8-14, 15-21, 22-28, 29-33
    zone5_dist = Counter()
    for item in data:
        z1 = sum(1 for x in item['red'] if 1 <= x <= 7)
        z2 = sum(1 for x in item['red'] if 8 <= x <= 14)
        z3 = sum(1 for x in item['red'] if 15 <= x <= 21)
        z4 = sum(1 for x in item['red'] if 22 <= x <= 28)
        z5 = sum(1 for x in item['red'] if 29 <= x <= 33)
        zone5_dist[f"{z1}-{z2}-{z3}-{z4}-{z5}"] += 1
    
    return {
        'zone3': zone_dist.most_common(10),
        'zone5': zone5_dist.most_common(10)
    }

def analyze_special(data):
    """8. 特殊形态分析"""
    # 同尾号
    same_tail_count = 0
    same_tail_details = Counter()
    
    for item in data:
        tails = [x % 10 for x in item['red']]
        tail_counter = Counter(tails)
        max_same = max(tail_counter.values())
        if max_same >= 2:
            same_tail_count += 1
            same_tail_details[f"{max_same}同尾"] += 1
    
    # 重号（与上一期相同的号码）
    repeat_count = 0
    repeat_dist = Counter()
    
    for i in range(1, len(data)):
        prev_red = set(data[i-1]['red'])
        curr_red = set(data[i]['red'])
        repeat = len(prev_red & curr_red)
        if repeat > 0:
            repeat_count += 1
            repeat_dist[f"{repeat}重号"] += 1
    
    return {
        'same_tail': same_tail_count,
        'same_tail_rate': same_tail_count / len(data) * 100,
        'same_tail_details': same_tail_details.most_common(5),
        'repeat': repeat_count,
        'repeat_rate': repeat_count / len(data) * 100,
        'repeat_dist': repeat_dist.most_common(5)
    }

def generate_report(data, output_path):
    """生成 markdown 报告"""
    hot_cold = analyze_hot_cold(data)
    omission = analyze_omission(data)
    odd_even = analyze_odd_even_big_small(data)
    sum_stats = analyze_sum(data)
    consecutive = analyze_consecutive(data)
    blue_stats = analyze_blue(data)
    zones = analyze_zones(data)
    special = analyze_special(data)
    
    report = f"""# 🦞 双色球数据分析报告

> 数据来源：中国福彩网 (https://www.zhcw.com)  
> 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 数据范围：{data[-1]['date']} 至 {data[0]['date']}  
> 总期数：**{len(data)} 期**

---

## 📊 目录

1. [热号冷号统计](#1-热号冷号统计)
2. [遗漏值分析](#2-遗漏值分析)
3. [奇偶/大小比例](#3-奇偶大小比例)
4. [和值走势](#4-和值走势)
5. [连号分析](#5-连号分析)
6. [蓝球专项](#6-蓝球专项)
7. [区间分布](#7-区间分布)
8. [特殊形态](#8-特殊形态)

---

## 1. 热号冷号统计

### 🔥 红球热号 TOP10

| 排名 | 号码 | 出现次数 | 出现频率 |
|------|------|----------|----------|
"""
    
    for i, (ball, count) in enumerate(hot_cold['red_hot'], 1):
        freq = count / len(data) * 100
        report += f"| {i} | **{ball:02d}** | {count} | {freq:.1f}% |\n"
    
    report += """
### 🧊 红球冷号 TOP10

| 排名 | 号码 | 出现次数 | 出现频率 |
|------|------|----------|----------|
"""
    
    for i, (ball, count) in enumerate(hot_cold['red_cold'], 1):
        freq = count / len(data) * 100
        report += f"| {i} | {ball:02d} | {count} | {freq:.1f}% |\n"
    
    report += """
### 🔵 蓝球热号 TOP5

| 排名 | 号码 | 出现次数 | 出现频率 |
|------|------|----------|----------|
"""
    
    for i, (ball, count) in enumerate(hot_cold['blue_hot'], 1):
        freq = count / len(data) * 100
        report += f"| {i} | **{ball:02d}** | {count} | {freq:.1f}% |\n"
    
    report += """
### 🧊 蓝球冷号 TOP5

| 排名 | 号码 | 出现次数 | 出现频率 |
|------|------|----------|----------|
"""
    
    for i, (ball, count) in enumerate(hot_cold['blue_cold'], 1):
        freq = count / len(data) * 100
        report += f"| {i} | {ball:02d} | {count} | {freq:.1f}% |\n"
    
    # 遗漏值分析
    report += f"""
---

## 2. 遗漏值分析

### 📍 当前遗漏期数（红球）

| 遗漏区间 | 号码数量 | 具体号码 |
|----------|----------|----------|
"""
    
    current_red = omission['current_red']
    omission_0_5 = [i for i, v in current_red.items() if v <= 5]
    omission_6_10 = [i for i, v in current_red.items() if 6 <= v <= 10]
    omission_11_20 = [i for i, v in current_red.items() if 11 <= v <= 20]
    omission_20_plus = [i for i, v in current_red.items() if v > 20]
    
    report += f"| 0-5 期 | {len(omission_0_5)} 个 | {', '.join(f'{i:02d}' for i in omission_0_5) or '无'} |\n"
    report += f"| 6-10 期 | {len(omission_6_10)} 个 | {', '.join(f'{i:02d}' for i in omission_6_10) or '无'} |\n"
    report += f"| 11-20 期 | {len(omission_11_20)} 个 | {', '.join(f'{i:02d}' for i in omission_11_20) or '无'} |\n"
    report += f"| 20 期以上 | {len(omission_20_plus)} 个 | {', '.join(f'{i:02d}' for i in omission_20_plus) or '无'} |\n"
    
    report += """
### 📍 当前遗漏期数（蓝球）

| 遗漏区间 | 号码数量 | 具体号码 |
|----------|----------|----------|
"""
    
    current_blue = omission['current_blue']
    omission_b_0_5 = [i for i, v in current_blue.items() if v <= 5]
    omission_b_6_10 = [i for i, v in current_blue.items() if 6 <= v <= 10]
    omission_b_11_20 = [i for i, v in current_blue.items() if 11 <= v <= 20]
    omission_b_20_plus = [i for i, v in current_blue.items() if v > 20]
    
    report += f"| 0-5 期 | {len(omission_b_0_5)} 个 | {', '.join(f'{i:02d}' for i in omission_b_0_5) or '无'} |\n"
    report += f"| 6-10 期 | {len(omission_b_6_10)} 个 | {', '.join(f'{i:02d}' for i in omission_b_6_10) or '无'} |\n"
    report += f"| 11-20 期 | {len(omission_b_11_20)} 个 | {', '.join(f'{i:02d}' for i in omission_b_11_20) or '无'} |\n"
    report += f"| 20 期以上 | {len(omission_b_20_plus)} 个 | {', '.join(f'{i:02d}' for i in omission_b_20_plus) or '无'} |\n"
    
    report += """
### 📈 历史最大遗漏（红球 TOP10）

| 排名 | 号码 | 最大遗漏期数 |
|------|------|--------------|
"""
    
    max_red_sorted = sorted(omission['max_red'].items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (ball, max_om) in enumerate(max_red_sorted, 1):
        report += f"| {i} | {ball:02d} | {max_om} |\n"
    
    report += """
### 📈 历史最大遗漏（蓝球 TOP5）

| 排名 | 号码 | 最大遗漏期数 |
|------|------|--------------|
"""
    
    max_blue_sorted = sorted(omission['max_blue'].items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (ball, max_om) in enumerate(max_blue_sorted, 1):
        report += f"| {i} | {ball:02d} | {max_om} |\n"
    
    # 奇偶/大小比例
    report += f"""
---

## 3. 奇偶/大小比例

### ⚖️ 奇偶比例分布

| 奇偶比 | 出现次数 | 出现频率 |
|--------|----------|----------|
"""
    
    for ratio, count in odd_even['odd_even']:
        freq = count / len(data) * 100
        report += f"| {ratio} | {count} | {freq:.1f}% |\n"
    
    report += """
### ⚖️ 大小比例分布（大号 17-33，小号 1-16）

| 大小比 | 出现次数 | 出现频率 |
|--------|----------|----------|
"""
    
    for ratio, count in odd_even['big_small']:
        freq = count / len(data) * 100
        report += f"| {ratio} | {count} | {freq:.1f}% |\n"
    
    # 和值走势
    report += f"""
---

## 4. 和值走势

### 📊 和值统计

| 统计项 | 数值 |
|--------|------|
| 最小和值 | {sum_stats['min']} |
| 最大和值 | {sum_stats['max']} |
| 平均和值 | {sum_stats['avg']:.1f} |
| 和值范围 | {sum_stats['max'] - sum_stats['min']} |

### 📈 最近 10 期和值走势

"""
    
    for i, s in enumerate(sum_stats['recent_10'], 1):
        bar = '█' * (s // 5)
        report += f"第 {len(data) - 10 + i} 期：和值 **{s}** {bar}\n"
    
    report += """
### 🔝 最常见和值 TOP10

| 排名 | 和值 | 出现次数 |
|------|------|----------|
"""
    
    for i, (s, count) in enumerate(sum_stats['distribution'], 1):
        report += f"| {i} | {s} | {count} |\n"
    
    # 连号分析
    none_rate = consecutive['none'] / consecutive['total'] * 100
    two_rate = consecutive['two'] / consecutive['total'] * 100
    three_rate = consecutive['three'] / consecutive['total'] * 100
    four_rate = consecutive['four_plus'] / consecutive['total'] * 100
    
    report += f"""
---

## 5. 连号分析

### 🔗 连号出现情况

| 连号类型 | 出现次数 | 出现频率 |
|----------|----------|----------|
| 无连号 | {consecutive['none']} | {none_rate:.1f}% |
| 二连号 | {consecutive['two']} | {two_rate:.1f}% |
| 三连号 | {consecutive['three']} | {three_rate:.1f}% |
| 四连号及以上 | {consecutive['four_plus']} | {four_rate:.1f}% |

> 💡 **观察**：约 **{100 - none_rate:.1f}%** 的期数会出现至少一组连号，连号是常见形态！

---

## 6. 蓝球专项

### 🔵 蓝球分布 TOP10

| 排名 | 号码 | 出现次数 | 出现频率 |
|------|------|----------|----------|
"""
    
    for i, (ball, count) in enumerate(blue_stats['distribution'][:10], 1):
        freq = count / len(data) * 100
        report += f"| {i} | {ball:02d} | {count} | {freq:.1f}% |\n"
    
    odd_rate = blue_stats['odd'] / len(data) * 100
    even_rate = blue_stats['even'] / len(data) * 100
    big_rate = blue_stats['big'] / len(data) * 100
    small_rate = blue_stats['small'] / len(data) * 100
    
    report += f"""
### ⚖️ 蓝球奇偶分布

| 类型 | 出现次数 | 出现频率 |
|------|----------|----------|
| 奇数 | {blue_stats['odd']} | {odd_rate:.1f}% |
| 偶数 | {blue_stats['even']} | {even_rate:.1f}% |

### ⚖️ 蓝球大小分布（1-8 为小，9-16 为大）

| 类型 | 出现次数 | 出现频率 |
|------|----------|----------|
| 小号 (1-8) | {blue_stats['small']} | {small_rate:.1f}% |
| 大号 (9-16) | {blue_stats['big']} | {big_rate:.1f}% |

### 🔢 蓝球 012 路分布

| 路数 | 说明 | 出现次数 | 出现频率 |
|------|------|----------|----------|
| 0 路 | 除 3 余 0 (3,6,9,12,15) | {blue_stats['road0']} | {blue_stats['road0']/len(data)*100:.1f}% |
| 1 路 | 除 3 余 1 (1,4,7,10,13,16) | {blue_stats['road1']} | {blue_stats['road1']/len(data)*100:.1f}% |
| 2 路 | 除 3 余 2 (2,5,8,11,14) | {blue_stats['road2']} | {blue_stats['road2']/len(data)*100:.1f}% |

---

## 7. 区间分布

### 📍 三区分布（一区 1-11，二区 12-22，三区 23-33）

| 区间比 | 出现次数 | 出现频率 |
|--------|----------|----------|
"""
    
    for ratio, count in zones['zone3']:
        freq = count / len(data) * 100
        report += f"| {ratio} | {count} | {freq:.1f}% |\n"
    
    report += """
### 📍 五区分布（一区 1-7，二区 8-14，三区 15-21，四区 22-28，五区 29-33）

| 区间比 | 出现次数 | 出现频率 |
|--------|----------|----------|
"""
    
    for ratio, count in zones['zone5'][:15]:
        freq = count / len(data) * 100
        report += f"| {ratio} | {count} | {freq:.1f}% |\n"
    
    # 特殊形态
    report += f"""
---

## 8. 特殊形态

### 🎯 同尾号分析

| 统计项 | 数值 |
|--------|------|
| 出现同尾号的期数 | {special['same_tail']} |
| 同尾号出现率 | {special['same_tail_rate']:.1f}% |

#### 同尾号详情 TOP5

| 类型 | 出现次数 |
|------|----------|
"""
    
    for tail_type, count in special['same_tail_details']:
        report += f"| {tail_type} | {count} |\n"
    
    report += f"""
### 🔄 重号分析（与上一期重复的号码）

| 统计项 | 数值 |
|--------|------|
| 出现重号的期数 | {special['repeat']} |
| 重号出现率 | {special['repeat_rate']:.1f}% |

#### 重号数量分布 TOP5

| 类型 | 出现次数 |
|------|----------|
"""
    
    for rep_type, count in special['repeat_dist']:
        report += f"| {rep_type} | {count} |\n"
    
    report += f"""
---

## 📝 总结与建议

### 🔑 核心发现

1. **热号**：红球热号 TOP3 为 **{hot_cold['red_hot'][0][0]:02d}**、**{hot_cold['red_hot'][1][0]:02d}**、**{hot_cold['red_hot'][2][0]:02d}**
2. **冷号**：红球冷号 TOP3 为 **{hot_cold['red_cold'][0][0]:02d}**、**{hot_cold['red_cold'][1][0]:02d}**、**{hot_cold['red_cold'][2][0]:02d}**
3. **遗漏**：当前遗漏最长的红球是 **{max(current_red.items(), key=lambda x: x[1])[0]:02d}**（遗漏 {max(current_red.values())} 期）
4. **奇偶**：最常见的奇偶比是 **{odd_even['odd_even'][0][0]}**
5. **大小**：最常见的大小比是 **{odd_even['big_small'][0][0]}**
6. **和值**：平均和值为 **{sum_stats['avg']:.1f}**，常见范围 {sum_stats['avg']-10:.0f}-{sum_stats['avg']+10:.0f}
7. **连号**：约 **{100 - none_rate:.1f}%** 的期数会出现连号
8. **蓝球**：最热蓝球是 **{blue_stats['distribution'][0][0]:02d}**

### ⚠️ 重要提醒

> 🎰 **彩票是随机游戏，历史数据不能预测未来结果！**
> 
> 本分析仅供娱乐参考，请理性购彩，量力而行。
> 
> 祝好运！🍀

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*🦞 由 哦玛吉米哈吉米 生成*
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

def main():
    input_file = "/home/dancekey/.openclaw/workspace/data/ssq_history.txt"
    output_file = "/home/dancekey/.openclaw/workspace/reports/ssq_analysis_report.md"
    
    print("🦞 正在加载数据...")
    data = load_data(input_file)
    print(f"✅ 加载完成，共 {len(data)} 期数据")
    
    print("📊 正在分析...")
    generate_report(data, output_file)
    print(f"✅ 报告已保存至：{output_file}")

if __name__ == "__main__":
    main()
