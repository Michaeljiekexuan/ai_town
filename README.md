# 🏘️ AI 小镇角色生活系统

这是一个构建在 JSON + MCP + 多代理架构基础上的小镇角色模拟系统。每个角色拥有独立的生活节奏、目标、情绪、体力、金钱等状态，支持自动或交互式模拟其生活行为。

## 📦 项目结构
```
project/
├── human/ # 存储角色 JSON 状态数据
│ └── jack.json
│ └── anna.json
│ └── tom.json
│ └── emily.json
│ └── yuri.json
│
├── dataset/ 
│ └── foods.json # 食物菜单 JSON 数据
│ └── jods.json # 工作列表菜单
│ └── town_news.json # 新闻菜单
│
├── character_editor.py # 角色mcp工具
├── humen.py # 人物动作工具
├── jack.py # 角色启动工具
├── test.py # 角色测试工具
├── db_config.py # 内容存储数据库配置
├── db_utils.py # 存储工具
├── emily.py # 小镇新闻构造工具
├── app.py # flask启动 （对接前端页面）
├── serve.py # 套接字服务 （对接unity游戏）
│
├── main.py # 启动交互或自动仿真代理系统

```
## 🧠 角色模型（human/*.json）

每个角色包含以下字段：

```json
{
  "name": "anna",
  "age": 20,
  "gender": "female",
  "job": "图书管理员",
  "personality": {
    "introversion": 0.6,
    "friendliness": 0.95,
    "curiosity": 0.8
  },
  "language_style": "你说话有一点可爱，喜欢开玩笑、互怼。并且有点计较",
  "hobbies": [
    "喜欢运动",
    "享受美食",
    "购物"
  ],
  "physical": 13,
  "money": 640,
  "recent_emotion": 5,
  "today_jods": [
    {
      "job": "图书馆管理员",
      "time": "17:00",
      "location": "图书馆",
      "lose": {
        "physical": -1,
        "emotion": 1
      },
      "give": {
        "money": 60
      }
    },
    {
      "job": "与Jack在小镇公园散步放松，同时记录生活中的美好瞬间，为Yuri挑选礼物寻找灵感。",
      "time": "14:00",
      "location": "小镇公园",
      "lose": {
        "physical": -2
      },
      "give": {
        "money": 0
      }
    }
  ],
  "current_thought": "在查找隐私保护资料时，发现差分隐私技术可能适用于我们的小游戏！得赶紧和Jack讨论如何在收集口音样本时加入噪声扰动，既保护隐私又能保持趣味性~（核心训练时腹部好酸！但想到能和Jack讨论新点子就超兴奋！）",
  "daily_routine": {
    "08:00": "吃早餐并计划一天的活动，同时回顾昨天的工作进展和Jack讨论小游戏规则设计细节，适当休息放松心情",
    "12:00": "与Jack在小镇餐厅享用午餐，讨论关于AI艺术结合项目的创意方向，并分享各自的感受",
    "19:00": "休息：尝试用新学的蒜香番茄酱搭配意大利面，和Jack分享烹饪心得",
    "24:00": "睡觉",
    "18:00": "与Jack一起准备晚餐，并聊聊一天的感受，享受轻松愉快的时光",
  },
  "current_activity": "与Jack一起准备晚餐，并聊聊一天的感受，享受轻松愉快的时光",
  "goals": [
    "提升自己的绘画和设计能力",
    "和jack建立深厚的感情",
    "记录生活中的美好片刻",
  ],
  "location": "厨房",
  "relationship": {
    "jack": "男朋友"
  },
  "memory": [
    "[记忆总结于 2025-05-20]: ....."
  ]
}
```

## ⚙️ MCP 工具（可被角色调用）

| 工具名                                         | 功能              |
| ------------------------------------------- | --------------- |
| `update_location(name, location)`           | 更改角色当前位置        |
| `update_daily_routine_batch(name, updates)` | 批量更新日程          |
| `delete_daily_routine_batch(name, times)`   | 批量删除日程          |
| `update_physical(name, delta)`              | 调整体力值（最小1，最大10） |
| `update_emotion(name, delta)`               | 调整情绪等级（最小1，最大5） |
| `update_money(name, delta)`                 | 更改角色金钱值         |
| `manage_today_jobs(name, jobs)`             | 增删今天的工作安排       |
还有很多.....

## 🍱 食物系统
```json
{
  "name": "香煎三文鱼",
  "price": 80,
  "physical": 3,
  "emotion": 2,
  "description": "新鲜三文鱼煎至外酥里嫩，营养丰富"
}
```
食物可以影响：

1.physical: 体力值（1~10）

2.recent_emotion: 情绪等级（1~5）

3.money: 金钱减少

角色会根据当前状态选择合适食物（如情绪低优先选提情绪食物）。

## 👥 多角色交互
系统支持角色间自动对话
对话记录会自动写入数据库（MySQL），结构大致为：
```
CREATE TABLE conversation_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  agent1 VARCHAR(32),
  agent2 VARCHAR(32),
  content TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
## 🎯 状态更新逻辑建议
1.情绪值范围：1（糟糕）到 5（极好），低于 1 将被重设为 1

2.体力值范围：1 到 10，最低保持在 1

3.金钱无上限，可为负数（用于欠债逻辑扩展）

## 📌 后续可扩展方向
✅ 饥饿系统与能量消耗

✅ 角色职业成长与技能系统

✅ 食物库存与消耗逻辑

✅ 性格影响决策：节俭、享乐、冲动

✅ 自动日程生成（已实现）

🛠️ 事件触发与情境应变（如突发事故）

📱 Unity 渲染角色状态（通过 socket 连接）
