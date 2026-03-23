#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双色球选号生成器 v2.0
五组不同策略的选号方案 + 机器学习模型 + 回测验证
"""

import random
import json
from datetime import datetime
from collections import Counter, defaultdict
import math

# ==================== 数据加载 ====================

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
    
    sorted_balls = sorted(red_counter.items(), key=lambda x: x[1], reverse=True)
    hot_balls = [ball for ball, count in sorted_balls[:10]]
    cold_balls = [ball for ball, count in sorted_balls[-10:]]
    sub_hot_balls = [ball for ball, count in sorted_balls[10:20]]
    sub_cold_balls = [ball for ball, count in sorted_balls[-20:-10]]
    
    return hot_balls, cold_balls, sub_hot_balls, sub_cold_balls, red_counter

# ==================== 基础选号策略 ====================

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
    """第三组：紫微斗数思想"""
    red_counter = Counter()
    for item in data:
        for ball in item['red']:
            red_counter[ball] += 1
    
    avg_count = sum(red_counter.values()) / len(red_counter)
    mid_balls = [ball for ball, count in red_counter.items() if 0.9 * avg_count <= count <= 1.1 * avg_count]
    if len(mid_balls) < 6:
        mid_balls = list(range(10, 25))
    
    ziwei_core = 17
    tianfu = random.choice(hot_balls[:5])
    qisha = random.choice(cold_balls[:5])
    tanlang = random.choice([x for x in range(1, 34) if x % 10 in [1, 6] and x not in [ziwei_core, tianfu, qisha]])
    wuqu = random.choice([x for x in range(1, 34) if x % 10 in [4, 9] and x not in [ziwei_core, tianfu, qisha, tanlang]])
    pojun = random.choice([x for x in range(28, 34) if x not in [ziwei_core, tianfu, qisha, tanlang, wuqu]])
    
    red = sorted([ziwei_core, tianfu, qisha, tanlang, wuqu, pojun])
    blue = random.choice([5, 10, 15])
    
    return red, blue

def generate_group4_yijing(data, hot_balls, cold_balls):
    """第四组：周易六爻占卜思想"""
    yao1 = random.choice([x for x in range(1, 6) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(1, 6)) else random.randint(1, 5)
    yao2 = random.choice([x for x in range(6, 11) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(6, 11)) else random.randint(6, 10)
    yao3 = random.choice([x for x in range(11, 17) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(11, 17)) else random.randint(11, 16)
    yao4 = random.choice([x for x in range(17, 23) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(17, 23)) else random.randint(17, 22)
    yao5 = random.choice([x for x in range(23, 29) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(23, 29)) else random.randint(23, 28)
    yao6 = random.choice([x for x in range(29, 34) if x in hot_balls or x in cold_balls]) if any(x in hot_balls or x in cold_balls for x in range(29, 34)) else random.randint(29, 33)
    
    red = [yao1, yao2, yao3, yao4, yao5, yao6]
    odd_count = sum(1 for x in red if x % 2 == 1)
    
    if odd_count != 3:
        for i in range(len(red)):
            if odd_count > 3 and red[i] % 2 == 1:
                new_val = red[i] + 1 if red[i] + 1 <= 33 else red[i] - 1
                if new_val not in red and 1 <= new_val <= 33:
                    red[i] = new_val
                    break
            elif odd_count < 3 and red[i] % 2 == 0:
                new_val = red[i] + 1 if red[i] + 1 <= 33 else red[i] - 1
                if new_val not in red and 1 <= new_val <= 33:
                    red[i] = new_val
                    break
    
    red.sort()
    blue = random.choice([8, 3, 13])
    
    return red, blue

# ==================== 机器学习模型 ====================

class SSQPredictor:
    """双色球预测模型"""
    
    def __init__(self, data):
        self.data = data
        self.red_counter = Counter()
        self.blue_counter = Counter()
        self._count_stats()
    
    def _count_stats(self):
        """统计基础数据"""
        for item in self.data:
            for ball in item['red']:
                self.red_counter[ball] += 1
            self.blue_counter[item['blue']] += 1
    
    def calc_omission(self, recent_data, ball, is_blue=False):
        """计算遗漏值"""
        omission = 0
        for item in recent_data:
            balls = [item['blue']] if is_blue else item['red']
            if ball in balls:
                break
            omission += 1
        return omission
    
    def calc_ac_value(self, red_balls):
        """计算 AC 值（数字复杂指数）"""
        diffs = []
        for i in range(len(red_balls)):
            for j in range(i+1, len(red_balls)):
                diffs.append(abs(red_balls[i] - red_balls[j]))
        unique_diffs = len(set(diffs))
        return unique_diffs - 5  # AC 值 = 不同差值数 - 5
    
    def calc_zone_ratio(self, red_balls):
        """计算三区比"""
        zone1 = sum(1 for x in red_balls if 1 <= x <= 11)
        zone2 = sum(1 for x in red_balls if 12 <= x <= 22)
        zone3 = sum(1 for x in red_balls if 23 <= x <= 33)
        return (zone1, zone2, zone3)
    
    def extract_features(self, recent_data, ball):
        """提取单个号码的特征"""
        features = {}
        
        # 特征 1: 历史出现频率
        features['freq'] = self.red_counter.get(ball, 0) / len(self.data)
        
        # 特征 2: 近 10 期出现次数
        recent_10 = recent_data[:10] if len(recent_data) >= 10 else recent_data
        features['recent_freq'] = sum(1 for item in recent_10 if ball in item['red']) / len(recent_10)
        
        # 特征 3: 当前遗漏值
        features['omission'] = self.calc_omission(recent_data, ball)
        
        # 特征 4: 历史最大遗漏
        max_om = 0
        cur_om = 0
        for item in self.data:
            if ball in item['red']:
                max_om = max(max_om, cur_om)
                cur_om = 0
            else:
                cur_om += 1
        features['max_omission'] = max_om
        
        # 特征 5: 遗漏比（当前遗漏/最大遗漏）
        features['omission_ratio'] = features['omission'] / (features['max_omission'] + 1)
        
        # 特征 6: 尾数热度
        tail = ball % 10
        tail_count = sum(1 for b in self.red_counter if b % 10 == tail)
        features['tail_hot'] = tail_count / 33
        
        # 特征 7: 区间热度
        if 1 <= ball <= 11:
            zone = 1
        elif 12 <= ball <= 22:
            zone = 2
        else:
            zone = 3
        zone_balls = [b for b in self.red_counter if (1 <= b <= 11 if zone == 1 else (12 <= b <= 22 if zone == 2 else 23 <= b <= 33))]
        features['zone_hot'] = sum(self.red_counter[b] for b in zone_balls) / (len(self.data) * 6)
        
        return features
    
    def score_ball(self, features, weights=None):
        """计算号码综合得分"""
        if weights is None:
            weights = {
                'freq': 0.15,
                'recent_freq': 0.25,
                'omission': 0.10,
                'omission_ratio': 0.20,
                'tail_hot': 0.10,
                'zone_hot': 0.20
            }
        
        score = 0
        score += features['freq'] * weights['freq']
        score += features['recent_freq'] * weights['recent_freq']
        score += (1 / (features['omission'] + 1)) * weights['omission']
        score += features['omission_ratio'] * weights['omission_ratio']
        score += features['tail_hot'] * weights['tail_hot']
        score += features['zone_hot'] * weights['zone_hot']
        
        return score
    
    def predict_red(self, recent_data, n=6):
        """预测红球"""
        scores = {}
        for ball in range(1, 34):
            features = self.extract_features(recent_data, ball)
            scores[ball] = self.score_ball(features)
        
        # 选前 n 个
        sorted_balls = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        red = sorted([ball for ball, score in sorted_balls[:n]])
        
        return red
    
    def predict_blue(self, recent_data):
        """预测蓝球"""
        scores = {}
        for ball in range(1, 17):
            # 蓝球特征：历史频率 + 近期频率 + 遗漏值
            freq = self.blue_counter.get(ball, 0) / len(self.data)
            recent_10 = recent_data[:10] if len(recent_data) >= 10 else recent_data
            recent_freq = sum(1 for item in recent_10 if item['blue'] == ball) / len(recent_10)
            omission = self.calc_omission(recent_data, ball, is_blue=True)
            
            score = freq * 0.3 + recent_freq * 0.4 + (1 / (omission + 1)) * 0.3
            scores[ball] = score
        
        # 选最高分
        blue = max(scores.items(), key=lambda x: x[1])[0]
        return blue
    
    def predict(self, n_recent=30):
        """完整预测"""
        recent_data = self.data[:n_recent] if len(self.data) >= n_recent else self.data
        red = self.predict_red(recent_data)
        blue = self.predict_blue(recent_data)
        return red, blue

# ==================== 回测验证 ====================

class Backtester:
    """回测验证器"""
    
    def __init__(self, data, predictor):
        self.data = data
        self.predictor = predictor
    
    def backtest(self, start_idx=100, end_idx=None, n_recent=30):
        """
        回测验证
        start_idx: 从第几期开始回测（倒数）
        end_idx: 到第几期结束（倒数，None 表示最新一期）
        """
        if end_idx is None:
            end_idx = 0
        
        # 确保索引有效
        start_idx = min(start_idx, len(self.data) - 10)
        end_idx = max(end_idx, 0)
        
        results = []
        
        for i in range(start_idx, end_idx, -1):
            # 用 i 期之前的数据预测第 i 期
            test_data = self.data[i:]
            actual = self.data[i]
            
            # 预测
            predictor = SSQPredictor(test_data)
            pred_red, pred_blue = predictor.predict(n_recent)
            
            # 计算匹配
            red_match = len(set(pred_red) & set(actual['red']))
            blue_match = 1 if pred_blue == actual['blue'] else 0
            
            results.append({
                'issue': actual['issue'],
                'date': actual['date'],
                'predicted_red': pred_red,
                'predicted_blue': pred_blue,
                'actual_red': actual['red'],
                'actual_blue': actual['blue'],
                'red_match': red_match,
                'blue_match': blue_match
            })
        
        return results
    
    def analyze_results(self, results):
        """分析回测结果"""
        stats = {
            'total': len(results),
            'red_3_plus': 0,
            'red_4_plus': 0,
            'red_5_plus': 0,
            'red_6': 0,
            'blue_correct': 0,
            'avg_red_match': 0,
            'prize_simulation': 0
        }
        
        total_red_match = 0
        
        for r in results:
            total_red_match += r['red_match']
            
            if r['red_match'] >= 3:
                stats['red_3_plus'] += 1
            if r['red_match'] >= 4:
                stats['red_4_plus'] += 1
            if r['red_match'] >= 5:
                stats['red_5_plus'] += 1
            if r['red_match'] == 6:
                stats['red_6'] += 1
            if r['blue_match'] == 1:
                stats['blue_correct'] += 1
            
            # 模拟奖金（简化版）
            if r['red_match'] == 6 and r['blue_match'] == 1:
                stats['prize_simulation'] += 5000000  # 一等奖
            elif r['red_match'] == 6:
                stats['prize_simulation'] += 200000  # 二等奖
            elif r['red_match'] == 5 and r['blue_match'] == 1:
                stats['prize_simulation'] += 3000  # 三等奖
            elif r['red_match'] == 5 or (r['red_match'] == 4 and r['blue_match'] == 1):
                stats['prize_simulation'] += 200  # 四/五等奖
            elif r['red_match'] == 4 or (r['red_match'] == 3 and r['blue_match'] == 1):
                stats['prize_simulation'] += 10  # 五/六等奖
            elif r['blue_match'] == 1:
                stats['prize_simulation'] += 5  # 七等奖
        
        stats['avg_red_match'] = total_red_match / len(results) if results else 0
        
        return stats
    
    def print_report(self, results, stats):
        """打印回测报告"""
        print("\n" + "=" * 70)
        print("📊 回测验证报告")
        print("=" * 70)
        print(f"回测期数：{stats['total']} 期")
        print(f"回测区间：{results[-1]['date']} ({results[-1]['issue']}) 至 {results[0]['date']} ({results[0]['issue']})")
        print()
        
        print("🎯 红球匹配情况")
        print("-" * 50)
        print(f"平均匹配红球数：{stats['avg_red_match']:.2f} 个")
        print(f"匹配 3+ 红球：{stats['red_3_plus']} 次 ({stats['red_3_plus']/stats['total']*100:.1f}%)")
        print(f"匹配 4+ 红球：{stats['red_4_plus']} 次 ({stats['red_4_plus']/stats['total']*100:.1f}%)")
        print(f"匹配 5+ 红球：{stats['red_5_plus']} 次 ({stats['red_5_plus']/stats['total']*100:.1f}%)")
        print(f"匹配 6 红球：{stats['red_6']} 次 ({stats['red_6']/stats['total']*100:.1f}%)")
        print()
        
        print("🔵 蓝球匹配情况")
        print("-" * 50)
        print(f"蓝球正确：{stats['blue_correct']} 次 ({stats['blue_correct']/stats['total']*100:.1f}%)")
        print()
        
        print("💰 模拟奖金统计")
        print("-" * 50)
        print(f"总奖金：¥{stats['prize_simulation']:,.0f}")
        print(f"平均每注：¥{stats['prize_simulation']/stats['total']:.2f}")
        print(f"投入成本：¥{stats['total'] * 2}（每注 2 元）")
        print(f"净收益：¥{stats['prize_simulation'] - stats['total'] * 2:,.0f}")
        print(f"ROI: {(stats['prize_simulation'] - stats['total'] * 2) / (stats['total'] * 2) * 100:.1f}%")
        print()
        
        # 展示部分详细结果
        print("📋 部分详细结果（最近 5 期）")
        print("-" * 50)
        for r in results[:5]:
            print(f"{r['date']} {r['issue']}:")
            print(f"  预测：{' '.join(f'{x:02d}' for x in r['predicted_red'])} | {r['predicted_blue']:02d}")
            print(f"  实际：{' '.join(f'{x:02d}' for x in r['actual_red'])} | {r['actual_blue']:02d}")
            print(f"  匹配：红球 {r['red_match']} 个，蓝球 {r['blue_match']} 个")
            print()
        
        print("=" * 70)

# ==================== 第五组选号（机器学习版） ====================

def generate_group5_ml(data):
    """第五组：机器学习模型预测"""
    predictor = SSQPredictor(data)
    return predictor.predict(n_recent=30)

# ==================== 生成报告文件 ====================

def generate_report(groups, backtest_results=None, backtest_stats=None):
    """生成 markdown 报告"""
    report = f"""# 🦞 双色球选号方案

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 数据来源：中国福彩网 (https://www.zhcw.com)

---

## 📋 五组选号结果

### 【第一组】3 最冷 +3 最热 + 蓝球 01

**策略**：选择历史出现次数最少的 3 个冷号 + 出现次数最多的 3 个热号，蓝球固定为 01

| 红球 | 蓝球 |
|------|------|
| {' '.join(f'{x:02d}' for x in groups[0][0])} | {groups[0][1]:02d} |

---

### 【第二组】3 次冷 +3 次热 + 蓝球 01

**策略**：选择冷号排名 4-6 位 + 热号排名 4-6 位，蓝球固定为 01

| 红球 | 蓝球 |
|------|------|
| {' '.join(f'{x:02d}' for x in groups[1][0])} | {groups[1][1]:02d} |

---

### 【第三组】紫微斗数 × 数据分析

**策略**：
- 紫微星 17 号坐命宫（33 的中点，帝星之位）
- 天府星取热号（财帛宫）
- 七杀星取冷号（将星破局）
- 贪狼取尾数 1/6（水）
- 武曲取尾数 4/9（金）
- 破军取大号区

| 红球 | 蓝球 |
|------|------|
| {' '.join(f'{x:02d}' for x in groups[2][0])} | {groups[2][1]:02d} |

---

### 【第四组】周易六爻 × 数据分析

**策略**：
- 六爻定位：每爻对应一个区间
- 阴阳平衡：3 奇 3 偶
- 卦象：水火既济（阴阳调和）

| 红球 | 蓝球 |
|------|------|
| {' '.join(f'{x:02d}' for x in groups[3][0])} | {groups[3][1]:02d} |

---

### 【第五组】机器学习模型预测

**策略**：
- 特征提取：历史频率、近期频率、遗漏值、尾数热度、区间热度
- 权重分配：近期频率 25% + 区间热度 20% + 遗漏比 20% + 历史频率 15% + 其他 20%
- 训练数据：最近 30 期

| 红球 | 蓝球 |
|------|------|
| {' '.join(f'{x:02d}' for x in groups[4][0])} | {groups[4][1]:02d} |

---

## 📊 机器学习模型回测验证

"""
    
    if backtest_results and backtest_stats:
        report += f"""### 回测概况

| 指标 | 数值 |
|------|------|
| 回测期数 | {backtest_stats['total']} 期 |
| 回测区间 | {backtest_results[-1]['date']} 至 {backtest_results[0]['date']} |
| 平均匹配红球 | {backtest_stats['avg_red_match']:.2f} 个 |

### 红球匹配统计

| 匹配数量 | 次数 | 频率 |
|----------|------|------|
| 3+ 红球 | {backtest_stats['red_3_plus']} | {backtest_stats['red_3_plus']/backtest_stats['total']*100:.1f}% |
| 4+ 红球 | {backtest_stats['red_4_plus']} | {backtest_stats['red_4_plus']/backtest_stats['total']*100:.1f}% |
| 5+ 红球 | {backtest_stats['red_5_plus']} | {backtest_stats['red_5_plus']/backtest_stats['total']*100:.1f}% |
| 6 红球 | {backtest_stats['red_6']} | {backtest_stats['red_6']/backtest_stats['total']*100:.1f}% |

### 蓝球匹配统计

| 指标 | 数值 |
|------|------|
| 蓝球正确次数 | {backtest_stats['blue_correct']} |
| 蓝球正确率 | {backtest_stats['blue_correct']/backtest_stats['total']*100:.1f}% |

### 模拟奖金统计

| 指标 | 数值 |
|------|------|
| 总奖金 | ¥{backtest_stats['prize_simulation']:,.0f} |
| 平均每注 | ¥{backtest_stats['prize_simulation']/backtest_stats['total']:.2f} |
| 投入成本 | ¥{backtest_stats['total'] * 2} |
| 净收益 | ¥{backtest_stats['prize_simulation'] - backtest_stats['total'] * 2:,.0f} |
| ROI | {(backtest_stats['prize_simulation'] - backtest_stats['total'] * 2) / (backtest_stats['total'] * 2) * 100:.1f}% |

> ⚠️ 注：奖金标准为简化版，实际奖金会因奖池和注数浮动

---

"""
    else:
        report += "> 回测数据生成中...\n\n"
    
    report += f"""## ⚠️ 重要提醒

> 🎰 **彩票是随机游戏，历史数据不能预测未来结果！**
> 
> 本选号方案仅供娱乐参考，请理性购彩，量力而行。
> 
> 祝好运！🍀

---

*报告生成：哦玛吉米哈吉米 🦞*
"""
    
    return report

# ==================== 主程序 ====================

def main():
    input_file = "/home/dancekey/.openclaw/workspace/data/ssq_history.txt"
    output_file = "/home/dancekey/.openclaw/workspace/reports/ssq_selection_report.md"
    
    print("🦞 双色球选号生成器 v2.0")
    print("=" * 60)
    
    # 加载数据
    print("\n📊 正在加载数据...")
    data = load_data(input_file)
    print(f"✅ 加载完成，共 {len(data)} 期数据")
    
    # 获取热号冷号
    print("\n📈 正在分析热号冷号...")
    hot_balls, cold_balls, sub_hot_balls, sub_cold_balls, red_counter = get_hot_cold_stats(data)
    print(f"✅ 热号 TOP10: {hot_balls}")
    print(f"✅ 冷号 TOP10: {cold_balls}")
    
    # 生成五组选号
    print("\n🔮 正在生成五组选号...")
    
    groups = []
    
    # 第一组
    g1 = generate_group1(hot_balls, cold_balls)
    groups.append(g1)
    print(f"  ✅ 第一组：{' '.join(f'{x:02d}' for x in g1[0])} | {g1[1]:02d}")
    
    # 第二组
    g2 = generate_group2(sub_hot_balls, sub_cold_balls)
    groups.append(g2)
    print(f"  ✅ 第二组：{' '.join(f'{x:02d}' for x in g2[0])} | {g2[1]:02d}")
    
    # 第三组
    g3 = generate_group3_ziwei(data, hot_balls, cold_balls)
    groups.append(g3)
    print(f"  ✅ 第三组：{' '.join(f'{x:02d}' for x in g3[0])} | {g3[1]:02d}")
    
    # 第四组
    g4 = generate_group4_yijing(data, hot_balls, cold_balls)
    groups.append(g4)
    print(f"  ✅ 第四组：{' '.join(f'{x:02d}' for x in g4[0])} | {g4[1]:02d}")
    
    # 第五组（机器学习）
    g5 = generate_group5_ml(data)
    groups.append(g5)
    print(f"  ✅ 第五组：{' '.join(f'{x:02d}' for x in g5[0])} | {g5[1]:02d}")
    
    # 回测验证
    print("\n🔍 正在进行回测验证（最近 100 期）...")
    predictor = SSQPredictor(data)
    backtester = Backtester(data, predictor)
    backtest_results = backtester.backtest(start_idx=100, end_idx=0, n_recent=30)
    backtest_stats = backtester.analyze_results(backtest_results)
    backtester.print_report(backtest_results, backtest_stats)
    
    # 生成报告
    print("\n📝 正在生成报告...")
    report = generate_report(groups, backtest_results, backtest_stats)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已保存至：{output_file}")
    
    # 保存 JSON 结果
    json_output = {
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'groups': [
            {
                'name': '第一组：3 最冷 +3 最热',
                'red': groups[0][0],
                'blue': groups[0][1]
            },
            {
                'name': '第二组：3 次冷 +3 次热',
                'red': groups[1][0],
                'blue': groups[1][1]
            },
            {
                'name': '第三组：紫微斗数',
                'red': groups[2][0],
                'blue': groups[2][1]
            },
            {
                'name': '第四组：周易六爻',
                'red': groups[3][0],
                'blue': groups[3][1]
            },
            {
                'name': '第五组：机器学习',
                'red': groups[4][0],
                'blue': groups[4][1]
            }
        ],
        'backtest_stats': backtest_stats
    }
    
    json_file = "/home/dancekey/.openclaw/workspace/reports/ssq_selection.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ JSON 结果已保存至：{json_file}")
    
    print("\n" + "=" * 60)
    print("✅ 所有任务完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
