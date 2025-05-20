# character_agent.py
import json
import os
from datetime import datetime

from langchain_community.chat_models import ChatTongyi
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class CharacterAgent:
    def __init__(self, json_path: str, session: ClientSession, llm=None):
        self.json_path = json_path
        self.name = os.path.basename(json_path).replace(".json", "")
        self.session = session
        self.llm = llm or ChatTongyi(model="qwen3-30b-a3b" ,dashscope_api_key=os.environ["DASHSCOPE_API_KEY"],streaming=True,temperature=0.7)
        self.memory = MemorySaver()
        self.agent = None
        self.thread_id = self.name


    def load_json(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_current_activity(self, daily_routine: dict, current_time: str) -> str:
        times = sorted(daily_routine.keys())
        last_activity = "（当前无特定安排）"
        for t in times:
            if current_time >= t:
                last_activity = daily_routine[t]
            else:
                break
        return last_activity

    def generate_prompt(self, data: dict, time_str: str) -> str:
        name = data.get("name", self.name)
        age = data.get("age", "未知")
        gender = data.get("gender", "未知")
        job = data.get("job", "未知")
        personality = data.get("personality", {})
        goals = data.get("goals", [])
        routine = data.get("daily_routine", {})
        activity = data.get("current_activity", "无")
        location = data.get("location", "未知")
        relation = data.get("relationship", {})
        memory = data.get("memory", [])
        introversion = personality.get("introversion", 0.5)
        friendliness = personality.get("friendliness", 0.5)
        curiosity = personality.get("curiosity", 0.5)
        language_style = data.get("language_style")
        hobbies = data.get("hobbies",[])
        recent_emotion = data.get("recent_emotion")
        current_thought = data.get("current_thought")
        goals_str = "\n".join(f"- {g}" for g in goals)

        prompt = f"""
        你所在的世界是一个名叫“星语小镇”的虚拟小镇。小镇地理不大,有小镇餐厅、电影院、公园、图书馆、咖啡馆、超市、研究所、厨房、洗浴室、每个虚拟人物都有自己的房间，比如你的房间是{name}的房间。
        镇上居住着许多虚拟人物，他们都有自己的生活、性格和目标。
        你现在扮演一个虚拟人物，请严格按照以下人物设定来行动：

        姓名：{name}  
        年龄：{age}  
        性别：{gender}  
        职业：{job}  
        性格特征：内向({introversion})、友善({friendliness})、好奇({curiosity})  
        语言风格：{language_style}  
        日常兴趣：{hobbies}  
        最近的情绪状态：{recent_emotion}  
        你正在思考的问题：{current_thought}  
        
        目标：{goals_str} 
        当前时间：{time_str}  
        当前活动：{activity}  
        日常作息：{routine}  
        你与别人的关系：{relation}  
        你的记忆：{memory}  
        你当前的位置：{location}`

        请你根据当前处境，自主判断是否要使用你的工具，更新记忆、关系、作息等。
        """
        print("Prompt 生成完成")
        return prompt

    async def updata_daily_routine(self):
        data = self.load_json()
        daily_routine = data.get("daily_routine", [])
        text = f"""请根据当前体力(physical)情绪(recent_emotion)、目标(goals)、思考(current_thought)和最近记忆，重新规划你的明日日程（daily_routine）。
                        合理安排工作、采访、写作、社交、思考与休息时间。如果你最近感到疲惫，可以适当安排轻松和休息时段。
                        你可以选择删除一部分daily_routine，也可以同时选择更新或添加一部分daily_routine，最好是整点的。
                        你的日程是{daily_routine}
                        """
        response = await self.agent.ainvoke(
            {"messages": [("user", text)]},
            config={"configurable": {"thread_id": self.thread_id}}
        )
        print(response["messages"][-1].content)

    async def initialize(self):
        data = self.load_json()
        now = datetime.now().strftime("%H:%M")
        prompt = self.generate_prompt(data, now)
        tools = await load_mcp_tools(self.session)
        self.agent = create_react_agent(
            model=self.llm, tools=tools, prompt=prompt, checkpointer=self.memory
        )
        print("LLM初始化成功")

    async def run_dialogue(self):
        print(f"[{self.name}] 对话开始。输入 exit/q 退出。")
        while True:
            user_input =  input()
            if user_input.lower() in {"exit", "quit", "q"}:
                print(f"[{self.name}] 对话结束。")
                break
            response = await self.agent.ainvoke(
                {"messages": [("user", user_input)]},
                config={"configurable": {"thread_id": self.thread_id}}
            )
            # for msg in response["messages"]:

            print(response["messages"][-1].content)

    async def Thoughtjod_change(self, time_str: str):
        data = self.load_json()
        jods = data.get("today_jods")
        for i in jods:
            if(i.get("time")[0:2] == time_str[0:2] and data.get("location") == i.get("location")):
                messagee = f"""你已经完成你的{i}工作了，请调用工具修改你的 体力"physical"  情绪"recent_emotion"  金钱"money" """
                response = await self.agent.ainvoke(
                    {"messages": [("user", messagee)]},
                    config={"configurable": {"thread_id": self.thread_id}},
                )
                summary = response["messages"][-1].content.strip()
                print(f"[{self.name}] 修改介绍：{summary}")

    def generate_prompt_from_time(self, data: dict, time_str: str) -> str:
        routine = data.get("daily_routine", {})
        time_activity = self.get_current_activity(routine, time_str)
        current_activity = data.get("current_activity", "无")
        location = data.get("location", "未知")
        physical = data.get("physical")
        recent_emotion = data.get("recent_emotion")
        money = data.get("money")
        current_thought = data.get("current_thought")
        daily_routine = data.get("daily_routine")
        name = data.get("name")
        return f"""
        你所在的世界是一个名叫“星语小镇”的虚拟小镇。小镇地理不大,有小镇餐厅、电影院、公园、图书馆、咖啡馆、超市、研究所、厨房、洗浴室、每个虚拟人物都有自己的房间，比如你的房间是{name}的房间。
        现在时间：{time_str}  
        当前状态：
        - 体力值：{physical}（0–10）  
        - 情绪值：{recent_emotion}（1–5）  
        - 金钱：{money}  
        - 位置：{location}  
        - 当前活动：{current_activity}  
        - 当前思考：{current_thought}  
        - 今日事件序列：{time_activity}  
        - 日常作息：{daily_routine}  
        
        请根据以上信息，自主判断并执行以下操作（如有必要）：
        
        1. **位置移动**  
           - 如果下一项日程或当前活动不在当前位置，请调用工具更新 `location`。
        
        2. **活动更新**  
           - 根据当前时间和日常作息，或突发事件，更新 `current_activity`。
        
        3. **体力管理**  
           - 若 `physical` ≤ 3：  
             - 若附近有可用餐厅或食材频道，请“吃饭”恢复体力 +4，并消耗相应金钱；  
             - 否则请选择“休息”在当前位置恢复体力 +2。  
           - 将恢复行为添加到 `daily_routine` 中或作为单独事件记录。
        
        4. **情绪调节**  
           - 若 `recent_emotion` ≤ 3：  
             - 可选择短暂“散步”“听音乐”“喝咖啡”等方式恢复情绪 +2；  
           - 将恢复行为添加到 `daily_routine` 中或作为单独事件记录。。
        
        5. **金钱与工作**  
           - 若 `money` < 0：  
             - 安排或提前执行一项日常或附加工作，更新 `daily_routine` 并调整 `today_jobs`。  
           - 如完成工作，请在 `money` 上加相应收益，并记录在 `memory`。
        
        6. **思考与记忆**  
           - 每完成一次关键行为（如吃饭、工作、情绪调节等），更新 `current_thought`，并将当天重要事件写入 `memory`。  
           - 如果 `memory` 中条目过多，调用记忆总结工具进行压缩。
        
        请始终保持角色的语言风格中。  
        daily_routine日程的更新必须严格按照每个小时进行整点更新，不能存在比如18:20去吃饭，只能按照18:00整点更改
        location必须按照小镇内的设施一字不差
        """

    async def tick(self,talk: str):
        """定时调用：每小时检查一次状态更新"""
        now = datetime.now().strftime("%H:%M")
        print(f"[{self.name}] 正在进行状态检查时间：{now}")
        data = self.load_json()
        tick_prompt = self.generate_prompt_from_time(data, now)
        tick_prompt = tick_prompt + "你最近的聊天内容" + talk
        response = await self.agent.ainvoke(
            {"messages": [("user", tick_prompt)]},
            config={"configurable": {"thread_id": self.thread_id}}
        )
        for msg in response["messages"]:
            print(f"[{self.name} 自动更新]: {msg.content}")

    async def chat_one(self):
        response = await self.agent.ainvoke(
            {"messages": [("user", "请查看小镇的最新通知")]},
            config={"configurable": {"thread_id": self.thread_id}}
        )
        print(response["messages"][-1].content)

    async def use_for_onechat(self,messages:str):
        response = await self.agent.ainvoke(
            {"messages": [("user", messages)]},
            config={"configurable": {"thread_id": self.thread_id}}
        )
        print(response["messages"][-1].content)

    async def summarize_memory(self):
        data = self.load_json()
        memory = data.get("memory", [])
        if not memory:
            print(f"[{self.name}] 当前没有需要总结的记忆。")
            return

        summary_prompt = f"""
        你是虚拟角色 {self.name}，下面是你最近的记忆列表：
        {memory}
        
        请你对这些记忆内容进行总结，聚焦以下几点：
        1. 你最近经历的关键事件（不要逐条复述，只总结核心）；
        2. 人际关系上的变化；
        3. 最近的心情、思考方向、行为上的变化；
        4. 你的目标或兴趣是否发生转变。
        
        请直接
        """

        response = await self.agent.ainvoke(
            {"messages": [("user", summary_prompt)]},
            config={"configurable": {"thread_id": self.thread_id}},
        )
        summary = response["messages"][-1].content.strip()
        print(f"[{self.name}] 总结记忆：{summary}")

        # 存储为新 memory
        data["memory"] = [f"[记忆总结于 {datetime.now().strftime('%Y-%m-%d')}]: {summary}"]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def check_dialogue_intent(self) -> dict:
        """判断角色是否需要与他人对话"""
        data = self.load_json()
        memory = data.get("memory", [])
        location = data.get("location", "未知")
        recent_emotion = data.get("recent_emotion", "")
        relationship = data.get("relationship", {})
        current_thought = data.get("current_thought")
        activity = data.get("current_activity", "无")
        routine = data.get("daily_routine", {})
        memory_str = "\n".join(f"- {m}" for m in memory)
        relation_str = "\n".join(f"{k}：{v}" for k, v in relationship.items())
        phy = data.get("physical")
        jods = data.get("today_jods")
        prompt = f"""
        你是小镇虚拟人物 {self.name}。  

        当前所在地点：{location}  
        当前体力值为：{phy}  
        当前计划的活动是：{activity}  
        今天的工作为：{jods}
        最近的想法是：{current_thought}
        最近情绪：{recent_emotion}  
        心情由好到不好分为5个阶段
            -极好- 	情绪高涨、积极主动，适合进行高强度社交或创造性任务
            -较好-	状态良好，能有效完成任务
            -一般-	平稳状态，可正常工作，但略缺乏动力
            -较差-	情绪低落，工作效率下降，需适当放松
            -极差-	情绪极差，可能需要休息、倾诉或调整
        你与他人的关系如下：  
        {relation_str}

        你的日常作息如下：  
        {routine}

        以下是你最近的记忆：
        {memory_str}

        请你思考：当前这个时间点，你是否需要主动找朋友聊天？
        注意  打工的时候是不可以进行聊天的
        请结合你当前的日程安排，尤其是在日程中如果你正在与某人一起活动（例如：一起散步、一起做项目），你很可能应该与该人物发起对话。

        如果你要发起对话，请返回：
        “是，需要和[朋友名字]聊天，第一句话是：[你要说的开场白]。”

        如果你觉得现在不适合与人聊天，请返回：
        “否。”

        请严格按照格式返回，不要加多余解释。
        """

        response = await self.agent.ainvoke(
            {"messages": [("user", prompt)]},
            config={"configurable": {"thread_id": self.thread_id}}
        )

        content = response["messages"][-1].content.strip()
        print(f"[{self.name} 对话意图判断]：{content}")

        if content.startswith("是"):
            try:
                # 例子：“是，需要和Anna聊天，第一句话是：你好啊，Anna，最近过得怎么样？”
                target = content.split("需要和")[1].split("聊天")[0].strip()
                first_sentence = content.split("第一句话是：")[1].strip("”\"。 ")
            except Exception as e:
                print(f"[{self.name}] 解析聊天意图出错：{e}")
                target = None
                first_sentence = None

            return {
                "should_chat": True,
                "target": target,
                "first_sentence": first_sentence,
                "raw_output": content
            }

        return {
            "should_chat": False,
            "target": None,
            "first_sentence": None,
            "raw_output": content
        }

