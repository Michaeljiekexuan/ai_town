import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from human import CharacterAgent
from pathlib import Path
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
            name = "tom"
            agent1 = CharacterAgent(f"human/{name}.json", session)
            agent2 = CharacterAgent(f"human/yuri.json", session)
            await agent1.initialize()
            await agent2.initialize()
            await agent_talk(agent1,agent2,"你好，我是新来的小镇成员yuri")
            await agent1.tick()
            await agent2.tick()

async def agent_talk(agent1, agent2, initial_prompt: str):
    print(f"\n🧠 {agent1.name} starts speaking")
    message = f"{agent2.name}: {initial_prompt}"  # 初始加入名字
    for _ in range(4):
        # agent1 发言
        response1 = await agent1.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": agent1.thread_id}}
        )
        content1 = response1["messages"][-1].content
        message = f"{agent1.name}: {content1}"  # 👈 发言带名字
        print(message)

        # agent2 回复
        response2 = await agent2.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": agent2.thread_id}}
        )
        content2 = response2["messages"][-1].content
        message = f"{agent2.name}: {content2}"  # 👈 回复也带名字
        print(message)

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

asyncio.run(main())