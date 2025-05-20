import pymysql
from db_config import DB_CONFIG

def save_conversation(agent1_name, agent2_name, content):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = '''
            INSERT INTO agent_conversations (agent1, agent2, content)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(sql, (agent1_name, agent2_name, content))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 对话已保存至数据库。")
    except Exception as e:
        print(f"❌ 保存对话失败：{e}")