from mcp.server.fastmcp import FastMCP
import  json
import uuid
# 创建 MCP Server
mcp = FastMCP("小镇新闻编辑器")
@mcp.tool()
def add_town_news(news_type: str, title: str, content: str, location: str, tags: list) -> str:
    """
    添加一条新的小镇新闻。
    参数：
        news_type: 新闻类型（如“通知”、“活动预告”、“八卦”等）
        title: 新闻标题
        content: 新闻内容
        location: 发生地点
        tags: 标签列表，例如 ["提醒", "安全"]
    返回：
        操作结果字符串。
    """
    import uuid
    from datetime import datetime

    TOWN_DATA_PATH = "dataset/town_news.json"

    with open(TOWN_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    news_id = f"news_{str(uuid.uuid4())[:8]}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_item = {
        "id": news_id,
        "type": news_type,
        "title": title,
        "content": content,
        "timestamp": timestamp,
        "location": location,
        "tags": tags
    }

    data.setdefault("news", []).append(new_item)

    with open(TOWN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return f"已添加新闻：{title}（ID: {news_id}）"

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
def delete_town_news(news_id: str) -> str:
    """
    删除一条指定 ID 的小镇新闻。
    参数：
        news_id: 要删除的新闻 ID（如 news_001）
    返回：
        操作结果字符串。
    """
    TOWN_DATA_PATH = "dataset/town_news.json"

    with open(TOWN_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    original_len = len(data.get("news", []))
    data["news"] = [n for n in data.get("news", []) if n.get("id") != news_id]

    with open(TOWN_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if len(data["news"]) < original_len:
        return f"已删除新闻 ID：{news_id}"
    else:
        return f"未找到新闻 ID：{news_id}"
@mcp.tool()
def update_town_news(news_id: str, title: str = "", content: str = "", location: str = "", tags: list = []) -> str:
    """
    修改一条已有新闻的内容。
    参数：
        news_id: 要修改的新闻 ID
        title: 新标题（不修改则传空）
        content: 新内容（不修改则传空）
        location: 新地点（不修改则传空）
        tags: 新标签（不修改则传空 list）
    返回：
        操作结果字符串。
    """
    TOWN_DATA_PATH = "dataset/town_news.json"

    with open(TOWN_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for news in data.get("news", []):
        if news.get("id") == news_id:
            if title:
                news["title"] = title
            if content:
                news["content"] = content
            if location:
                news["location"] = location
            if tags:
                news["tags"] = tags

            with open(TOWN_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return f"已更新新闻 ID：{news_id}"

    return f"未找到新闻 ID：{news_id}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')