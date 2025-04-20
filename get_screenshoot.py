from mcp.server.fastmcp import FastMCP
import base64
import os
from openai import OpenAI
from PIL import ImageGrab
import numpy as np
import cv2
# 创建 MCP Server
mcp = FastMCP("屏幕截屏工具")

@mcp.tool()
def extract_text_from_screen() -> str:
    """从屏幕截图中识别出所有文本，按视觉顺序排列"""

    # 截取屏幕指定区域
    img = np.array(ImageGrab.grab())  # 简化
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    import io

    is_success, buffer = cv2.imencode(".jpg", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-0f14b0e7f51f414cb889972bb18ab359",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片是电脑屏幕截图，请你做以下任务："
                "- 从图像中识别出所有能看清的文字内容"
                "- 将这些文字按屏幕位置顺序排列输出（可以编号）"
                "无需其他描述，只需要尽可能准确和全面的提取文字内容。"},
                {"type": "image_url",
                 "image_url": {
                     # 注意这里的前缀格式
                     "url": f"data:image/jpeg;base64,{base64_image}"
                 }}
            ]
        }]
    )
    return completion.model_dump_json()


@mcp.tool()
def analyse_screen_full() -> str:
    """对屏幕截图进行全面分析：提取文字、分析布局、识别界面类型"""

    # 截取屏幕指定区域
    img = np.array(ImageGrab.grab())  # 简化
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    import io

    is_success, buffer = cv2.imencode(".jpg", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-0f14b0e7f51f414cb889972bb18ab359",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
                    这是一张电脑屏幕截图，请你分以下几个方面对图片进行详细分析：
                    
                    1. 识别并按顺序提取其中的文本内容，包括网页、按钮、弹窗等。
                    2. 描述屏幕内容的布局和结构，例如左侧是否为菜单，中间是否为网页内容。
                    3. 判断该截图属于什么类型的界面（网页、软件、IDE、设置界面等）。
                    4. 如果有特殊元素（如对话框、警告框、输入框等），请特别指出并说明其作用。
                    
                    请使用条目清晰、有层次的格式输出，确保信息完整。
                    """},
                {"type": "image_url",
                 "image_url": {
                     # 注意这里的前缀格式
                     "url": f"data:image/jpeg;base64,{base64_image}"
                 }}
            ]
        }]
    )
    return completion.model_dump_json()


@mcp.tool()
def identify_software_ui() -> str:
    """分析屏幕界面类型（网页/软件/IDE）和界面结构"""

    # 截取屏幕指定区域
    img = np.array(ImageGrab.grab())  # 简化
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    import io

    is_success, buffer = cv2.imencode(".jpg", img)
    base64_image = base64.b64encode(buffer).decode("utf-8")
    client = OpenAI(
        # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
        api_key="sk-0f14b0e7f51f414cb889972bb18ab359",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-vl-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
                    请分析这张电脑屏幕截图：
                    
                    - 提取所有可见的文字信息，并按照视觉顺序输出（从上到下，从左到右）
                    - 分析界面的大致用途（是网页、编程IDE、聊天软件、设置页面等）
                    - 描述界面的组成结构（是否有侧边栏、顶部栏、主区域等）
                    - 如果可以，请推测用户当前正在进行什么任务
                    
                    要求：分析尽可能详细、准确，输出结构清晰。
                    """},
                {"type": "image_url",
                 "image_url": {
                     # 注意这里的前缀格式
                     "url": f"data:image/jpeg;base64,{base64_image}"
                 }}
            ]
        }]
    )
    return completion.model_dump_json()
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')