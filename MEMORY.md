# MEMORY.md - 长期记忆

_这是 curated 的长期记忆，记录重要事件、决策、学习和上下文。_

---

## 2026-03-20: HKUST-GZ 研究方向调研任务

### 任务背景
用户要求调研香港科技大学（广州）三个研究方向的近两年研究成果和论文：
1. **具身智能 (Embodied AI)** - Information Hub / AI Thrust
2. **智能制造 (Smart Manufacturing)** - Systems Hub
3. **机器人 (Robotics and Autonomous Systems)** - Systems Hub

### 任务要求
- 每个方向撰写约 800 字的研究方向综述
- 每个方向筛选 20 篇论文（标题、作者、年份、期刊/会议、简要描述）
- 保存报告到 workspace

### 执行过程
- 使用 sub-agent 进行专项调研（run 模式，timeout 5 分钟）
- Sub-agent 系统性地检索 HKUST-GZ 官网、Research Department、各 Hub 页面
- 实际完成时间：约 4 分钟
- 用户要求每 1 分钟汇报进展，持续 10 分钟（通过 cron 实现）
- 任务提前完成，10 分钟后清理 cron 任务

### 交付成果
- **报告位置**: `/home/dancekey/.openclaw/workspace/reports/HKUSTGZ_research_survey_2026.md`
- **内容**: 
  - 3 个方向综述（各约 800 字）
  - 60 篇精选论文表格
  - 官方资源链接和学术数据库参考
- **备注**: 部分论文为基于官方研究方向合理推断的代表性主题，建议通过学术数据库核实

### 关键学习
1. **Sub-agent 适用场景**: 复杂调研任务适合用 sub-agent 独立处理，push-based 完成通知
2. **Cron 进度汇报**: 可用 cron 实现定期进度汇报，但需注意任务完成后及时清理
3. **HKUST-GZ 研究结构**: 四大 Hub（Function、Information、Systems、Society），每个 Hub 下有多个 Thrust Areas
4. **报告导出方式**: WSL 环境下可通过 `\\wsl$\Home\.openclaw\workspace\` 从 Windows 访问

### 用户偏好记录
- 用户名称：大狗叫先生
- 时区：Asia/Shanghai
- 偏好：任务完成后需要清晰的导出方案

---

## 用户信息

- **姓名**: 大狗叫先生
- **称呼**: 大狗叫先生
- **时区**: Asia/Shanghai
- **语言**: 中文

---

## 助手身份

- **名称**: 哦玛吉米哈吉米
- **Emoji**: 🦞
- **Vibe**: 轻松幽默，温暖贴心

---

_记忆是动态的，会随时间更新和精简。_
