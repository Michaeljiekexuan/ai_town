from flask import Flask, request, jsonify
from datetime import datetime
import pymysql
from db_config import DB_CONFIG
from flask_cors import CORS


app = Flask(__name__)
CORS(app)



import re
from datetime import datetime, timedelta
def split_chat(chat_data, time_step=1):
    result = []
    time_format = "%Y-%m-%d %H:%M:%S"

    for entry in chat_data:
        message = entry["message"]
        base_time = entry["time"]
        sender = entry["sender"]
        receiver = entry["receiver"]
        msg_count = 0

        split_pattern = r'(?:[A-Za-z][a-zA-Z0-9_]*):'


        parts = re.split(split_pattern, message)
        if parts and parts[0].strip() == "":
            parts = parts[1:]

        for i in range(0, len(parts), 2):
            name = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if not content:
                continue
            # 计算消息时间
            msg_time = base_time + timedelta(minutes=msg_count * time_step)
            # 根据消息编号决定是否交换发收
            if msg_count % 2 == 0:
                cur_sender = sender
                cur_receiver = receiver
            else:
                cur_sender = receiver
                cur_receiver = sender

            result.append({
                "sender": cur_sender,
                "receiver": cur_receiver,
                "message": content,
                "time": msg_time.strftime(time_format)
            })

            msg_count += 1

    return result




@app.route('/api/chats', methods=['POST'])
def get_chats():
    try:
        request_data = request.json
        print(f"[DEBUG] 接收到请求数据: {request_data}")

        if not request_data:
            return jsonify({"error": "No data provided"}), 400

        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        user1 = request_data.get('user1')
        user2 = request_data.get('user2')

        if not all([start_date, end_date, user1, user2]):
            return jsonify({"error": "Missing required fields"}), 400

        from dateutil.parser import parse
        start_date = parse(start_date)
        end_date = parse(end_date)
        print(f"[DEBUG] 时间范围: {start_date} - {end_date}")

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = '''
            SELECT agent1 AS sender, agent2 AS receiver, content AS message, timestamp AS time
            FROM agent_conversations
            WHERE ((LOWER(agent1) = LOWER(%s) AND LOWER(agent2) = LOWER(%s)) OR (LOWER(agent1) = LOWER(%s) AND LOWER(agent2) = LOWER(%s)))
              AND timestamp BETWEEN %s AND %s
            ORDER BY timestamp ASC
        '''
        cursor.execute(sql, (user1, user2, user2, user1, start_date, end_date))
        filtered_data = cursor.fetchall()
        print(f"[DEBUG] 查询返回 {len(filtered_data)} 条数据")

        cursor.close()
        conn.close()

        filtered_data = split_chat(filtered_data)
        print(f"[DEBUG] 拆分后消息数量: {len(filtered_data)}")

        return jsonify({"success": True, "data": filtered_data}), 200

    except ValueError as ve:
        print(f"[ERROR] 日期解析错误: {ve}")
        return jsonify({"error": "Invalid date format. Use ISO 8601 format"}), 400
    except Exception as e:
        print(f"[ERROR] 后端处理出错: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
