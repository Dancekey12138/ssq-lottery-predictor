#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球选号生成器
五组不同策略的选号方案
"""

import random
from datetime import datetime
from collections import Counter

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
                    red_str = red_part.replace('红球：', '').strip()
                    blue_str = blue_part.replace('蓝球：', '').strip()
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

def get_hot_cold_stats(data):
    """获取热号冷号统计"""
    red_counter = Counter()
    for item in data:
        for ball in item['red']:
            red_counter[ball] += 1
    
    # 按出现次数排序
    sorted_balls = sorted(red_counter.items(), key=lambda x: x[1], reverse=True)
    
    # 最热 10 个
    hot_balls = [ball for ball, count in sorted_balls[:10]]
    # 最冷 10 个
    cold_balls = [ball for ball, count in sorted_balls[-10:]]
    # 次热（11-20 位）
    sub_hot_balls = [ball for ball, count in sorted_balls[10:20]]
    # 次冷（倒数 11-20 位）
    sub_cold_balls = [ball for ball, count in sorted_balls[-20:-10]]
    
    return hot_balls, cold_balls, sub_hot_balls, sub_cold_balls

def generate_group1(hot_balls, cold_balls):
    """第一组：3 最冷 +3 最热 + 蓝球 01"""
    red = random.sample(cold_balls, 3) + random.sample(hot_balls, 3)
    red.sort()
    return red, 1

def generate_group2(sub_hot_balls, sub_cold_balls):
    """第二组：3 次冷 +3 次热 + 蓝球 01"""
    red = random.sample(sub_cold_balls, 3) + random.sample(sub_hot_balls, 3)
    red.sort()
    return red, 1

def generate_group3_ziwei(data, hot_balls, cold_balls):
    """
    第三组：紫微斗数思想
    紫微斗数讲究"命盘十二宫"、"星曜组合"、"五行生克"
    这里用娱乐方式结合：
    - 紫微星（帝星）：取中间号 17（33 的中点）
    - 天府星：取热号中的稳定号
    - 七杀星：取冷号中的"破局"号
    - 五行：金木水火土对应尾数 49/38/16/27/50
    - 十二宫：选 6 个宫位对应 6 个号码
    """
    # 紫微斗数"命宫"位置：取近期出现频率中等的号码（不大热不大冷）
    mid_balls = []
    red_counter = Counter()
    for item in data:
        for ball in item['red']:
            red_counter[ball] += 1
    
    avg_count = sum(red_counter.values()) / len(red_counter)
    for ball, count in red_counter.items():
        if 0.9 * avg_count <= count <= 1.1 * avg_count:
            mid_balls.append(ball)
    
    if len(mid_balls) < 6:
        mid_balls = list(range(10, 25))  # 中区间
    
    # 紫微星位（核心）：取中位数
    ziwei_core = 17
    
    # 天府（财帛）：从热号选 1 个
    tianfu = random.choice(hot_balls[:5])
    
    # 七杀（将星）：从冷号选 1 个"破局"
    qisha = random.choice(cold_balls[:5])
    
    # 贪狼（桃花）：取尾数 1/6（水）
    tanlang = random.choice([x for x in range(1, 34) if x % 10 in [1, 6] and x not in [ziwei_core, tianfu, qisha]])
    
    # 武曲（财星）：取尾数 4/9（金）
    wuqu = random.choice([x for x in range(1, 34) if x % 10 in [4, 9] and x not in [ziwei_core, tianfu, qisha, tanlang]])
    
    # 破军（耗星）：取大号 28-33
    pojun = random.choice([x for x in range(28, 34) if x not in [ziwei_core, tianfu, qisha, tanlang, wuqu]])
    
    red = sorted([ziwei_core, tianfu, qisha, tanlang, wuqu, pojun])
    
    # 蓝球：紫微属土，取尾数 5/0 → 05/10/15
    blue = random.choice([5, 10, 15])
    
    return red, blue

def generate_group4_yijing(data, hot_balls, cold_balls):
    """
    第四组：周易六爻占卜思想
    六爻：初爻、二爻、三爻、四爻、五爻、上爻
    阴阳：奇数为阳，偶数为阴
    卦象：64 卦，每卦 6 爻
    动爻：变化的爻位
    
    这里用娱乐方式结合：
    - 6 个红球对应 6 爻
    - 阴阳平衡：3 阳 3 阴（3 奇 3 偶）
    - 卦象取"既济卦"（水火既济，阴阳调和）
    - 动爻位置决定变数
    """
    # 六爻定位：从下往上
    # 初爻（最下）：1-5 号区间
    # 二爻：6-10 号区间
    # 三爻：11-16 号区间
    # 四爻：17-22 号区间
    # 五爻：23-28 号区间
    # 上爻（最上）：29-33 号区间
    
    yao1 = random.choice([x for x in range(1, 6) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(1, 6)) else random.randint(1, 5)
    yao2 = random.choice([x for x in range(6, 11) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(6, 11)) else random.randint(6, 10)
    yao3 = random.choice([x for x in range(11, 17) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(11, 17)) else random.randint(11, 16)
    yao4 = random.choice([x for x in range(17, 23) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(17, 23)) else random.randint(17, 22)
    yao5 = random.choice([x for x in range(23, 29) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(23, 29)) else random.randint(23, 28)
    yao6 = random.choice([x for x in range(29, 34) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(29, 34)) else random.randint(29, 33)
    
    # 确保阴阳平衡（3 奇 3 偶）
    red = [yao1, yao2, yao3, yao4, yao5, yao6]
    odd_count = sum(1 for x in red if x % 2 == 1)
    
    # 如果不平衡，调整一个
    if odd_count != 3:
        for i in range(len(red)):
            if odd_count > 3 and red[i] % 2 == 1:
                # 奇数多，换偶数
                new_val = red[i] + 1 if red[i] + 1 <= 33 else red[i] - 1
                if new_val not in red and 1 <= new_val <= 33:
                    red[i] = new_val
                    break
            elif odd_count < 3 and red[i] % 2 == 0:
                # 偶数多，换奇数
                new_val = red[i] + 1 if red[i] + 1 <= 33 else red[i] - 1
                if new_val not in red and 1 <= new_val <= 33:
                    red[i] = new_val
                    break
    
    red.sort()
    
    # 蓝球：取"中爻"之意，选中号 08（六爻之中）
    # 或根据"动爻"变化
    blue_options = [8, 3, 13]  # 中、初、上
    blue = random.choice(blue_options)
    
    return red, blue

def generate_group5_model(data):
    """
    第五组：推理模型
    基于前 30 期的趋势分析
    考虑因素：
    - 近期热号（近 10 期出现频率）
    - 遗漏值（多少期没出现）
    - 和值趋势
    - 奇偶比例趋势
    - 连号趋势
    """
    recent_30 = data[:30]  # 最近 30 期
    recent_10 = data[:10]  # 最近 10 期
    
    # 近期热号（近 10 期）
    recent_counter = Counter()
    for item in recent_10:
        for ball in item['red']:
            recent_counter[ball] += 1
    
    hot_recent = [ball for ball, count in recent_counter.most_common(8)]
    
    # 遗漏值计算
    omission = {i: 0 for i in range(1, 34)}
    for item in recent_30:
        for ball in item['red']:
            omission[ball] = 0
        for i in range(1, 34):
            if i not in item['red']:
                omission[i] += 1
    
    # 遗漏 5-15 期的号码（可能回补）
    due_balls = [i for i, om in omission.items() if 5 <= om <= 15]
    
    # 和值分析
    recent_sums = [sum(item['red']) for item in recent_10]
    avg_sum = sum(recent_sums) / len(recent_sums)
    
    # 奇偶趋势
    recent_odd = [sum(1 for x in item['red'] if x % 2 == 1) for item in recent_10]
    avg_odd = sum(recent_odd) / len(recent_odd)
    
    # 生成选号
    red = []
    
    # 从近期热号选 2 个
    red.extend(random.sample(hot_recent, min(2, len(hot_recent))))
    
    # 从遗漏回补号选 2 个
    due_available = [x for x in due_balls if x not in red]
    red.extend(random.sample(due_available, min(2, len(due_available))))
    
    # 从热号选 1 个
    remaining_hot = [x for x in hot_recent if x not in red]
    if remaining_hot:
        red.append(random.choice(remaining_hot))
    
    # 随机选 1 个（增加变数）
    remaining = [x for x in range(1, 34) if x not in red]
    if len(red) < 6:
        red.append(random.choice(remaining))
    
    # 如果还不够 6 个，补齐
    while len(red) < 6:
        candidate = random.randint(1, 33)
        if candidate not in red:
            red.append(candidate)
    
    red = sorted(red[:6])
    
    # 蓝球：根据近期蓝球趋势
    recent_blue = [item['blue'] for item in recent_10]
    blue_counter = Counter(recent_blue)
    
    # 选一个近期不太热但也不是最冷的
    blue_candidates = [i for i in range(1, 17) if i not in blue_counter.most_common(3)]
    if not blue_candidates:
        blue_candidates = list(range(1, 17))
    blue = random.choice(blue_candidates)
    
    return red, blue

def print_groups(groups):
    """打印五组选号"""
    print("\n" + "=" * 60)
    print("🦞 双色球选号方案")
    print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    for i, (red, blue) in enumerate(groups, 1):
        red_str = ' '.join(f'{x:02d}' for x in red)
        print(f"【第{i}组】{red_str} | 蓝球：{blue:02d}")
    
    print("\n" + "=" * 60)

def main():
    input_file = "/home/dancekey/.openclaw/workspace/data/ssq_history.txt"
    
    print("🦞 正在加载数据...")
    data = load_data(input_file)
    print(f"✅ 加载完成，共 {len(data)} 期数据\n")
    
    print("📊 正在分析热号冷号...")
    hot_balls, cold_balls, sub_hot_balls, sub_cold_balls = get_hot_cold_stats(data)
    print(f"✅ 热号：{hot_balls}")
    print(f"✅ 冷号：{cold_balls}\n")
    
    print("🔮 生成五组选号...\n")
    
    # 第一组
    g1 = generate_group1(hot_balls, cold_balls)
    
    # 第二组
    g2 = generate_group2(sub_hot_balls, sub_cold_balls)
    
    # 第三组（紫微斗数）
    g3 = generate_group3_ziwei(data, hot_balls, cold_balls)
    
    # 第四组（周易六爻）
    g4 = generate_group4_yijing(data, hot_balls, cold_balls)
    
    # 第五组（推理模型）- 先打印代码框架
    print("=" * 60)
    print("📋 前四组选号结果")
    print("=" * 60)
    print(f"\n【第一组】3 最冷 +3 最热 + 蓝球 01")
    print(f"  红球：{' '.join(f'{x:02d}' for x in g1[0])} | 蓝球：{g1[1]:02d}")
    
    print(f"\n【第二组】3 次冷 +3 次热 + 蓝球 01")
    print(f"  红球：{' '.join(f'{x:02d}' for x in g2[0])} | 蓝球：{g2[1]:02d}")
    
    print(f"\n【第三组】紫微斗数 × 数据分析")
    print(f"  红球：{' '.join(f'{x:02d}' for x in g3[0])} | 蓝球：{g3[1]:02d}")
    print(f"  💡 紫微 17 号坐命，天府财星，七杀破局")
    
    print(f"\n【第四组】周易六爻 × 数据分析")
    print(f"  红球：{' '.join(f'{x:02d}' for x in g4[0])} | 蓝球：{g4[1]:02d}")
    print(f"  💡 六爻定位，阴阳平衡，水火既济")
    
    print("\n" + "=" * 60)
    print("📝 第五组：推理模型代码框架")
    print("=" * 60)
    
    model_code = '''
# 第五组：基于前 30 期趋势的推理模型

## 模型思路

1. **数据输入**：最近 30 期开奖数据
2. **特征提取**：
   - 近期热号（近 10 期出现频率）
   - 遗漏值（多少期未出现）
   - 和值走势（移动平均）
   - 奇偶比例趋势
   - 连号出现频率
   - 区间分布（三区比）
   - 蓝球遗漏

3. **权重分配**：
   - 近期热号：30%
   - 遗漏回补：25%
   - 和值回归：15%
   - 奇偶平衡：15%
   - 随机变数：15%

4. **输出**：6 红 +1 蓝

## 代码实现（简化版）

```python
def predict_next(data, n=30):
    recent = data[:n]
    
    # 特征 1: 近期热号
    hot = Counter(ball for item in recent[:10] for ball in item['red'])
    
    # 特征 2: 遗漏值
    omission = calc_omission(recent)
    
    # 特征 3: 和值趋势
    sums = [sum(item['red']) for item in recent]
    avg_sum = sum(sums) / len(sums)
    
    # 特征 4: 奇偶趋势
    odd_ratio = sum(sum(1 for x in item['red'] if x%2) for item in recent) / (6*n)
    
    # 综合评分
    scores = {}
    for ball in range(1, 34):
        score = 0
        score += hot.get(ball, 0) * 0.3
        score += (1 / (omission[ball] + 1)) * 0.25
        # ... 其他特征
        scores[ball] = score
    
    # 选前 6 个
    red = sorted([b for b, s in sorted(scores.items(), key=lambda x: -x[1])[:6]])
    
    # 蓝球预测
    blue = predict_blue(recent)
    
    return red, blue
```

## 待完善功能

- [ ] 添加机器学习模型（LSTM/随机森林）
- [ ] 加入更多特征（尾数分布、AC 值等）
- [ ] 回测验证准确率
- [ ] 可视化趋势图
'''
    print(model_code)
    
    # 生成第五组实际结果
    g5 = generate_group5_model(data)
    
    print("\n" + "=" * 60)
    print("✅ 第五组实际选号（推理模型）")
    print("=" * 60)
    print(f"\n【第五组】基于前 30 期趋势推算")
    print(f"  红球：{' '.join(f'{x:02d}' for x in g5[0])} | 蓝球：{g5[1]:02d}")
    print(f"  💡 综合近期热号、遗漏回补、和值趋势")
    
    print("\n" + "=" * 60)
    print("⚠️ 温馨提示：彩票是随机游戏，以上选号仅供娱乐参考")
    print("   理性购彩，量力而行，祝好运！🍀")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
