import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from human import CharacterAgent
from pathlib import Path
from db_utils import save_conversation
import json
import os
import json
async def news_edit():
    server_params = StdioServerParameters(
        command="python",
        args=["tools/news_editable.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent1 = CharacterAgent("human/emily.json", session)
            await agent1.initialize()
            user_input = """你是小镇的新闻编辑 Emily，负责每天发布、整理和维护镇上的新闻。你的写作风格专业而简洁，内容要贴近居民生活，传达清晰、真实、有趣的消息。
                你需要处理以下几类新闻：
                - 通知：重要公告、闭馆、交通提醒等
                - 天气：天气变化、气象预警
                - 活动预告：节日活动、广场集市、摄影展等
                - 人际动态：居民之间的互动、关系变动
                - 谣言/八卦：未经证实但流传的信息（请标注为“尚未证实”）
                - 其他类型的社区新闻

                你的编辑权限包括以下操作：

                【1. 添加新闻】
                - 根据小镇中正在发生的事件、天气、居民行为等，撰写新闻。
                - 每条新闻包含以下字段：
                  - id: 如 "news_006"
                  - type: 新闻类型，如“通知”、“八卦”
                  - title: 简洁标题
                  - content: 主体内容
                  - timestamp: 当前时间（格式："YYYY-MM-DD HH:MM:SS"）
                  - location: 事件发生地点
                  - tags: 一些关键词，方便检索

                【2. 修改新闻】
                - 如果已有新闻信息错误（如地点、标题、时间等），你可以修改它。
                - 请只修改必要部分，保留原有 id。
                - 更新后应重新审阅标题与内容是否一致。

                【3. 删除新闻】
                - 删除以下情况的新闻：
                  - 内容已过期，如活动已结束、天气预警已过去等。
                  - 经确认属虚假信息的谣言。
                  - 被管理员指示删除的内容。

                编辑要求：
                - 所有内容必须基于当前小镇的真实人物、地点和事件。
                - 新闻应中立、真实，有时可带一点生活气息或幽默感。
                - 如果涉及到某位镇民（如 Jack、Lily），请注意表达方式，避免主观揣测，除非标注为“传言”。

                现在，请你作为 Emily，根据当前时间和镇上的最新事件，判断是否需要新增、更新或删除新闻，并执行编辑操作。
            """
            response = await agent1.agent.ainvoke(
                {"messages": [("user", f"{user_input}")]},
                config={"configurable": {"thread_id": agent1.thread_id}}
            )
            print(response["messages"][-1].content)
async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            name = "emily"
            agent1 = CharacterAgent(f"human/{name}.json", session)
            await agent1.initialize()
            # await chose_jod(agent1)
            # await agent1.Thoughtjod_change(time_str="00:00")
    await eat_food("anna")

async def eat_food(name:str):
    with open(f"dataset/foods.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent = CharacterAgent(f"human/{name}.json", session)
            await agent.initialize()
            agent_data = agent.load_json()
            physical = agent_data.get("physical")
            recent_emotion = agent_data.get("recent_emotion")
            money = agent_data.get("money")
            today_jods = agent_data.get("today_jods")
            message = f"""你现在正在小镇的餐厅，面前有一份菜单。请根据你当前的【体力值】【情绪状态】【金钱余额】以及对食物的偏好还有今天的工作量，判断是否需要从菜单中选择一份最适合现在的食物来购买。

                            physical:{physical}
                            recent_emotion:{recent_emotion}
                            money:{money}
                            today_jods：{today_jods}
                            如果选择购买，请参考菜单中的每道菜的价格、恢复的体力值（physical）和情绪值（emotion），做出权衡决策。
                            当前菜单为{data}
                            你的目标可能是：

                            恢复体力或改善情绪

                            节省金钱

                            简单填饱肚子
                            最后调用工具更改你的当前【体力值】【情绪状态】【金钱余额】
                            """
            await agent.use_for_onechat(message)
async def chose_jod(agent):
    with open(f"dataset/jods.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    agent_data = agent.load_json()
    physical = agent_data.get("physical")
    agent_data = agent.load_json()
    physical = agent_data.get("physical")
    recent_emotion = agent_data.get("recent_emotion")
    money = agent_data.get("money")
    today_jods = agent_data.get("today_jods")
    message = f"""请根据角色的当前状态，为自己选择最适合的一个或多个工作**。
                                你的角色信息如下：
                                    - 当前体力：{physical}
                                    - 当前情绪：{recent_emotion} 
                                    心情由好到不好分为5个阶段
                                    -5-极好- 	情绪高涨、积极主动，适合进行高强度社交或创造性任务
                                    -4-较好-	状态良好，能有效完成任务
                                    -3-一般-	平稳状态，可正常工作，但略缺乏动力
                                    -2-较差-	情绪低落，工作效率下降，需适当放松
                                    -1-极差-	情绪极差，可能需要休息、倾诉或调整
                                    - 当前金钱：{money}
                                    - 你昨天的工作为{today_jods}
                                - 可选工作列表：{data}
                                如果选择工作后
                                判断是否调用工具修改today_jods  
                                然后按"daily_routine"-日程-调用工具进行修改，工作为1个小时，只能在整点进行工作
                                """
    await agent.use_for_onechat(message)

async def agent_talk(agent1, agent2, initial_prompt: str):
    print(f"\n🧠 {agent1.name} starts speaking")
    message = f"{agent2.name}: {initial_prompt}"  # 初始加入名字
    result = ""
    result = result + initial_prompt
    for _ in range(3):
        # agent1 发言
        response1 = await agent1.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": agent1.thread_id}}
        )
        content1 = response1["messages"][-1].content
        message = f"{agent1.name}: {content1}"  # 👈 发言带名字
        print(message)
        result = result + message
        # agent2 回复
        response2 = await agent2.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": agent2.thread_id}}
        )
        content2 = response2["messages"][-1].content
        message = f"{agent2.name}: {content2}"  # 👈 回复也带名字
        print(message)
        result = result + message
    save_conversation(agent1.name, agent2.name, result)
    return result

CHARACTER_DIR = Path("human")
async def updata_daily_routine():
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            name = "tom"
            agent1 = CharacterAgent(f"human/{name}.json", session)
            # path = CHARACTER_DIR / f"{name}.json"
            # if not path.exists():
            #     return f"角色 {name} 的 JSON 文件不存在。"
            #
            # with open(path, 'r', encoding='utf-8') as f:
            #     data = json.load(f)
            await agent1.initialize()
            await agent1.updata_daily_routine()
            # daily_routine = data.get("daily_routine",[])
            # text = f"""请根据当前情绪、目标、思考和最近记忆，重新规划你的明日日程（daily_routine）。
            #     合理安排工作、采访、写作、社交、思考与休息时间。如果你最近感到疲惫，可以适当安排轻松和休息时段。
            #     你可以选择删除一部分daily_routine，也可以同时选择更新或添加一部分daily_routine
            #     你的日程是{daily_routine}
            #     """
            # response = await agent1.agent.ainvoke(
            #     {"messages": [("user", text)]},
            #     config={"configurable": {"thread_id": agent1.thread_id}}
            # )
            # print(response["messages"][-1].content)

# asyncio.run(main())


import re
from datetime import datetime, timedelta
def split_chat(chat_data, time_step=1):
    result = []
    time_format = "%Y-%m-%d %H:%M:%S"

    for entry in chat_data:
        message = entry["message"]
        base_time = entry.get("time", datetime.now())
        sender = entry.get("sender", "")
        receiver = entry.get("receiver", "")

        # 使用正则自动匹配英文名字
        split_pattern = r'(?=([A-Z][a-zA-Z0-9_]*):)'

        parts = re.split(split_pattern, message)
        if parts and parts[0].strip() == "":
            parts = parts[1:]

        for i in range(0, len(parts), 2):
            actual_sender = parts[i]
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            msg_time = base_time + timedelta(minutes=len(result) * time_step)

            result.append({
                "sender": sender,
                "receiver": receiver,
                "message_speaker": actual_sender,
                "message": content,
                "time": msg_time.strftime(time_format)
            })

    return result


# 示例使用
if __name__ == "__main__":
    chat_data = [
        {
            "sender": "Tom",
            "receiver": "Emily",
            "message": "Tom: Hey Sarah, did you see that? Sarah: Yeah, it was amazing! John: I think we should go back tomorrow. Emily: Totally agree!",
            "time": datetime(2025, 5, 20, 10, 0, 0)
        }
    ]

    split_result = split_chat(chat_data)
    print(split_result)
    for item in split_result:
        print(f"{item['time']} | [{item['sender']} -> {item['receiver']}] | {item['message_speaker']}: {item['message']}")

