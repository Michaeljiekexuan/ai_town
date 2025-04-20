# main.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from human import CharacterAgent
from langchain_mcp_adapters.tools import load_mcp_tools



import time
from datetime import datetime, timedelta

async def job(talk: str):
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for i in names:
                agent = CharacterAgent(f"human/{i}.json", session)
                await agent.initialize()
                await agent.tick(talk)
names = ["jack","anna","tom","emily","yuri"]
async def updata_daily_routine():
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for i in names:
                agent = CharacterAgent(f"human/{i}.json", session)
                await agent.initialize()
                await agent.updata_daily_routine()

async def person_job(name: str,talk: str):
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent1 = CharacterAgent(f"human/{name}.json", session)
            await agent1.initialize()
            await agent1.tick(talk)

async def meres():
    server_params = StdioServerParameters(
        command="python",
        args=["character_editor.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            for i in names:
                agent = CharacterAgent(f"human/{i}.json", session)
                await agent.initialize()
                await agent.summarize_memory()

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
    return result

async def wait_for_next_hour():
    while True:
        now = datetime.now()
        # 计算下一个整点时间（比如，3:00，4:00，5:00等）
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        # 计算等待的秒数
        sleep_time = (next_hour - now).total_seconds()
        print(f"当前时间：{now}, 等待 {int(sleep_time)} 秒直到下一个整点...")
        time.sleep(sleep_time)  # 等待到下一个整点
        await job("")
        server_params = StdioServerParameters(
            command="python",
            args=["character_editor.py"],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for i in names:
                    agent1 = CharacterAgent(f"human/{i}.json", session)
                    await agent1.initialize()
                    chat_decision = await agent1.check_dialogue_intent()
                    if chat_decision["should_chat"]:
                        agent2 = CharacterAgent(f"human/{chat_decision['target']}.json", session)
                        await agent2.initialize()
                        result = await agent_talk(agent2, agent1, chat_decision['first_sentence'])
                        await person_job(i,result)
                        await person_job(chat_decision['target'],result)
                    else:
                        print(f"[{i}] 当前不想与人聊天。")

if __name__ == "__main__":
    # 开始小镇
    # asyncio.run(wait_for_next_hour())


    # 每日记忆总结
    # asyncio.run(meres())


    #明天的日程修改
    asyncio.run(updata_daily_routine())



