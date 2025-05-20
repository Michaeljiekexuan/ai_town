# main.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from human import CharacterAgent
from langchain_mcp_adapters.tools import load_mcp_tools
import json


import time
from datetime import datetime, timedelta
from db_utils import save_conversation

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
                            如果有必要也可以加入你的记忆memory
                            """
            await agent.use_for_onechat(message)

async def chose_jod():
    with open(f"dataset/jods.json", "r", encoding="utf-8") as f:
        data = json.load(f)
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
                                -5-极好- 情绪高涨、积极主动，适合进行高强度社交或创造性任务
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
    save_conversation(agent1.name, agent2.name, result)
    return result

async def run():
    await job("")
    if (datetime.now().strftime("%H") == "12" or datetime.now().strftime("%H") == "6"):
        for i in names:
            await eat_food(i)
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
                await agent1.Thoughtjod_change(time_str=datetime.now().strftime("%H:%M"))
                chat_decision = await agent1.check_dialogue_intent()
                if chat_decision["should_chat"]:
                    agent2 = CharacterAgent(f"human/{chat_decision['target']}.json", session)
                    await agent2.initialize()
                    result = await agent_talk(agent2, agent1, chat_decision['first_sentence'])

                    await person_job(i, result)
                    await person_job(chat_decision['target'], result)
                else:
                    print(f"[{i}] 当前不想与人聊天。")
async def wait_for_next_hour():
    while True:
        now = datetime.now()
        # 计算下一个整点时间（比如，3:00，4:00，5:00等）
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        # 计算等待的秒数
        sleep_time = (next_hour - now).total_seconds()
        print(f"当前时间：{now}, 等待 {int(sleep_time)} 秒直到下一个整点...")
        print("test1")
        time.sleep(sleep_time)  # 等待到下一个整点
        await job("")
        if(datetime.now().strftime("%H")=="12" or datetime.now().strftime("%H")=="6"):
            for i in names:
                await eat_food(i)
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
                    await agent1.Thoughtjod_change(time_str=datetime.now().strftime("%H:%M"))
                    chat_decision = await agent1.check_dialogue_intent()
                    if chat_decision["should_chat"]:
                        agent2 = CharacterAgent(f"human/{chat_decision['target']}.json", session)
                        await agent2.initialize()
                        result = await agent_talk(agent2, agent1, chat_decision['first_sentence'])

                        await person_job(i,result)
                        await person_job(chat_decision['target'],result)
                    else:
                        print(f"[{i}] 当前不想与人聊天。")

#




if __name__ == "__main__":
    # 开始小镇
    asyncio.run(run())
    asyncio.run(wait_for_next_hour())

    # # 选择工作
    # asyncio.run(chose_jod())
    #
    # # 每日记忆总结
    # asyncio.run(meres())
    #
    #
    # # 明天的日程修改
    # asyncio.run(updata_daily_routine())



