import os
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server 实例
mcp = FastMCP("角色 JSON 编辑工具")

# 设置角色 JSON 文件所在的目录
CHARACTER_DIR = Path("human")
@mcp.tool()
def delete_daily_routine_batch(name: str, times: list) -> str:
    """
    批量删除角色 daily_routine 中指定时间点的事件。

    参数：
        name: 角色名称（对应 JSON 文件名）
        times: 要删除的时间点列表（格式为 "HH:mm"）

    返回：
        操作结果描述字符串
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "daily_routine" not in data:
        return f"{name} 的日程中没有任何事件。"

    deleted = []
    for time in times:
        if time in data["daily_routine"]:
            deleted.append(f"{time}：{data['daily_routine'].pop(time)}")

    if not deleted:
        return "没有找到需要删除的时间点。"

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已删除以下日程事件：\n" + "\n".join(deleted)
# 工具：设置角色在特定时间的日程安排
@mcp.tool()
def update_daily_routine_batch(name: str, updates: dict) -> str:
    """
    批量更新或添加角色 daily_routine 中的多个时间点的事件。

    参数：
        name: 角色名称（对应 JSON 文件名）
        updates: 要更新的键值对（时间: 新事件）

    返回：
        操作结果描述字符串
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "daily_routine" not in data:
        data["daily_routine"] = {}

    changes = []
    for time, new_event in updates.items():
        original = data["daily_routine"].get(time)
        data["daily_routine"][time] = new_event
        if original:
            changes.append(f"{time}：'{original}' → '{new_event}'")
        else:
            changes.append(f"{time}：新增 '{new_event}'")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return "已批量更新如下时间点的日程：\n" + "\n".join(changes)


# 工具：设置角色在当前时间的活动安排
@mcp.tool()
def set_current_activity(name: str, activity: str) -> str:
    """
    设置角色在当前时间应该去做的活动。
    参数：
        name: 角色名称（对应 JSON 文件名）
        activity: 活动内容
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["current_activity"] = activity

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 的当前活动改为：{activity}"
# 工具：为角色添加新的目标
@mcp.tool()
def add_goal(name: str, goal: str) -> str:
    """
    为角色添加新的目标。
    参数：
        name: 角色名称（对应 JSON 文件名）
        goal: 新的目标内容
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data.setdefault("goals", [])
    if goal not in data["goals"]:
        data["goals"].append(goal)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已为 {name} 添加新目标：{goal}"

# 工具：更新角色的性格特征值
@mcp.tool()
def update_personality(name: str, trait: str, value: float) -> str:
    """
    更新角色的性格特征值。
    参数：
        name: 角色名称（对应 JSON 文件名）
        trait: 性格特征名称（例如 'introversion'）
        value: 新的特征值（0.0 到 1.0 之间）
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if trait not in ["introversion", "friendliness", "curiosity"]:
        return f"无法识别的性格特征：{trait}。"

    data.setdefault("personality", {})[trait] = value

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 的性格特征 {trait} 更新为：{value:.2f}"
@mcp.tool()
def add_memory(name: str, memory: str) -> str:
    """
    为角色添加新的记忆条目。
    参数：
        name: 角色名称（对应 JSON 文件名）
        memory: 要添加的记忆内容
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data.setdefault("memory", []).append(memory)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已为 {name} 添加记忆：{memory}"


@mcp.tool()
def read_town_news(filter: str = "") -> dict:
    """
    获取小镇当天的新闻和通知。
    参数：
        filter: 关键词过滤新闻内容，如“天气”、“公告”、“八卦”。为空则返回所有新闻。
    返回：
        包含 weekday 和符合条件的 news 列表。
    """
    TOWN_DATA_PATH = "dataset/town_news.json"

    with open(TOWN_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_news = data.get("news", [])
    weekday = data.get("weekday", "未知")

    if filter:
        filtered = [
            n for n in all_news if filter in n["type"] or filter in n["title"] or filter in n["content"]
        ]
    else:
        filtered = all_news

    return {
        "weekday": weekday,
        "news": filtered
    }
@mcp.tool()
def update_relationship(name: str, person: str, relation: str) -> str:
    """
    更新角色与其他人物的关系。
    参数：
        name: 角色名称（对应 JSON 文件名）
        person: 其他人物的名称
        relation: 与该人物的关系描述
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data.setdefault("relationship", {})[person] = relation

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 与 {person} 的关系更新为：{relation}"
@mcp.tool()
def update_recent_emotion(name: str, recent_emotion: str) -> str:
    """
    更新角色当前的心情。
    参数：
        name: 角色名称（对应 JSON 文件名）
        recent_emotion: 当前心情描述
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["recent_emotion"] = recent_emotion

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 当前的心情更新为：{recent_emotion}"

@mcp.tool()
def update_current_thought(name: str, current_thought: str) -> str:
    """
    更新角色当前正在思考的内容。
    参数：
        name: 角色名称（对应 JSON 文件名）
        current_thought: 最近思考的问题、内容或想法
    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data["current_thought"] = current_thought

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 当前的思考内容更新为：{current_thought}"

@mcp.tool()
def update_location(name: str, location: str) -> str:
    """
    更新角色当前位置。

    参数：
        name: 角色名称（对应 JSON 文件名）
        location: 当前人物应该所在的位置（如“电影院”、“公园”）

    返回：
        操作结果的字符串描述
    """
    path = CHARACTER_DIR / f"{name}.json"
    if not path.exists():
        return f"角色 {name} 的 JSON 文件不存在。"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 设置 location 字段
    data["location"] = location

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已将 {name} 的当前位置更新为：{location}"


# 启动 MCP 服务器
if __name__ == "__main__":
    mcp.run(transport='stdio')
