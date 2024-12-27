import socket
import threading
import mysql.connector
import json
from datetime import datetime

# 服务器配置
HOST = 'localhost'
PORT = 10086

# 连接到数据库
db = mysql.connector.connect(
    host="localhost",
    user="Haerxile",
    password="200518",
    database="COMM",
    consume_results=True 
)
cursor = db.cursor()

# 存储客户端连接
clients = {}

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def handle_client(conn, addr):
    print(f"新的连接来自 {addr}")
    try:
        while True:
            # 接收消息长度
            msg_length = conn.recv(4)
            if not msg_length:
                break
            msg_length = int.from_bytes(msg_length, byteorder='big')
            # 接收实际消息
            msg = conn.recv(msg_length).decode()
            print(f"收到消息: {msg} 来自 {addr}")
            
            # 解析消息（假设使用JSON格式）
            data = json.loads(msg)
            action = data.get("action")
            
            if action == "login":
                username = data.get("username")
                email = username
                password = data.get("password")
                # 验证用户
                cursor.execute("SELECT idUserInfo, username, is_admin, password FROM UserInfo WHERE username = %s OR email = %s", (username, email))
                user = cursor.fetchone()
                if user:
                    user_id, username, is_admin, right_pass = user
                    if password == right_pass:
                        # 登录成功
                        response = {"action": "login", "status": "success", "user_id": user_id, "is_admin": is_admin, "username": username}
                        clients[user_id] = conn
                    else:
                        response = {"action": "login", "status": "pass_fail", "message": "密码错误"}
                else:
                    response = {"action": "login", "status": "no_user", "message": "用户不存在，请先注册"}
                send_message(conn, response)
                
            elif action == "register":
                username = data.get("username")
                email = data.get("email")
                password = data.get("password")
                college = data.get("college")
                bio = data.get("bio")
                # 检查用户是否已存在
                cursor.execute("SELECT idUserInfo FROM UserInfo WHERE username = %s OR email = %s", (username, email))
                user = cursor.fetchone()
                if user:
                    response = {"action": "register", "status": "user_exists", "message": "用户已存在"}
                else:
                    # 插入用户到数据库
                    cursor.execute("INSERT INTO UserInfo (username, password, college, email, bio) VALUES (%s, %s, %s, %s, %s)", (username, password, college, email, bio))
                    db.commit()
                    response = {"action": "register", "status": "success", "message": "注册成功"}
                send_message(conn, response)
            
            elif action == "send_message":
                sender_id = data.get("sender_id")
                sender_name = None
                chat_id = data.get("chat_id")
                content = data.get("content")
                # 获取发送者名称
                cursor.execute("SELECT username FROM UserInfo WHERE idUserInfo = %s", (sender_id,))
                sender_name = cursor.fetchone()
                db.commit()
                if sender_name is not None:
                    sender_name = sender_name[0]
                else:
                    response = {"action": "receive_message", "status": "fail", "message": "发送失败，非法用户"}
                    send_message(conn, response)
                    continue
                # 插入消息到数据库
                cursor.execute("INSERT INTO ChatMessages (idBoardList, sender_id, sender_name, content, timestamp) VALUES (%s, %s, %s, %s, NOW())", (chat_id, sender_id, sender_name, content))
                db.commit()
                # 转发消息给所有参与该聊天的用户
                cursor.execute("SELECT user_id FROM UserAnnounceDiagram WHERE announce_id = %s", (chat_id,))
                participants = cursor.fetchall()
                for participant in participants:
                    pid = participant[0]
                    if pid in clients:
                        response = {
                            "action": "receive_message",
                            "status": "success",
                            "sender_id": sender_id,
                            "sender_name": sender_name,
                            "chat_id": chat_id,
                            "content": content,
                            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        send_message(clients[pid], response)
                        
            elif action == "load_recent_messages":
                chat_id = data.get("chat_id")
                user_id = data.get("user_id")
                timestamp = data.get("timestamp")  # 客户端传递的时间戳（可选）
                
                # 查询最近的消息
                query = """
                    SELECT sender_id, sender_name, content, timestamp 
                    FROM ChatMessages 
                    WHERE idBoardList = %s 
                    ORDER BY timestamp ASC
                    LIMIT 20
                """
                db.commit()
                cursor.execute(query, (chat_id,))
                messages = cursor.fetchall()
                db.commit()
                
                # 格式化消息
                formatted_messages = [
                    {
                        "sender_id": msg[0],
                        "sender_name": msg[1],
                        "content": msg[2],
                        "timestamp": msg[3].strftime('%Y-%m-%d %H:%M:%S')
                    } for msg in messages
                ]
                print(f"Debug - formatted_messages: {formatted_messages}")  # Debug line
                
                response = {
                    "action": "load_recent_messages",
                    "status": "success",
                    "chat_id": chat_id,
                    "messages": formatted_messages
                }
                send_message(conn, response)
                
            elif action == "refresh_older_messages":
                chat_id = data.get("chat_id")
                user_id = data.get("user_id")
                oldest_timestamp = data.get("oldest_timestamp")  # 客户端传递的最旧消息时间戳
                oldest_timestamp = datetime.strptime(oldest_timestamp, '%Y-%m-%d %H:%M:%S')
                
                # 查询比 oldest_timestamp 更早的消息
                query = """
                    SELECT sender_id, sender_name, content, timestamp 
                    FROM ChatMessages 
                    WHERE idBoardList = %s AND timestamp < %s 
                    ORDER BY timestamp ASC 
                    LIMIT 20
                """
                db.commit()
                cursor.execute(query, (chat_id, oldest_timestamp))
                messages = cursor.fetchall()
                db.commit()
                
                # 格式化消息
                formatted_messages = [
                    {
                        "sender_id": msg[0],
                        "sender_name": msg[1],
                        "content": msg[2],
                        "timestamp": msg[3].strftime('%Y-%m-%d %H:%M:%S')
                    } for msg in messages
                ]
                print(f"Debug - formatted_messages: {formatted_messages}")  # Debug line
                
                response = {
                    "action": "refresh_older_messages",
                    "status": "success",
                    "chat_id": chat_id,
                    "messages": formatted_messages
                }
                send_message(conn, response)
                        
            elif action == "show_announcement_detail":
                announcement_id = data.get("announcement_id")
                user_id = data.get("user_id")
                user_in = None
                print(f"Debug - announcement_id: {announcement_id}, user_id: {user_id}")  # Debug line
                # 查询公告详情
                cursor.execute("SELECT headline, content FROM BoardList WHERE idBoardList = %s", (announcement_id,))
                headline, content = cursor.fetchone()
                db.commit()
                print(f"Debug - headline: {headline}, content: {content}")  # Debug line
                cursor.execute("SELECT SQL_NO_CACHE * FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
                if user_in is not None:
                    user_in = None
                user_in = cursor.fetchone()
                db.commit()
                print(f"Debug - user_in: {user_in}")  # Debug line
                if content:
                    response = {
                        "action": "show_announce_detail",
                        "status": "success",
                        "announcement_id": announcement_id,
                        "title": headline,
                        "content": content,
                        "is_add_in": user_in is not None  # Fixed: True if user_in exists, False otherwise
                    }
                else:
                    response = {"action": "show_announce_detail", "status": "fail", "message": "获取公告详情失败"}
                send_message(conn, response)
                
            elif action == "refresh_announcement":
                cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
                announcements = cursor.fetchall()
                db.commit()
                # 从 UserAnnounceDiagram 中更新 join_num
                for announcement in announcements:
                    cursor.execute("SELECT COUNT(*) FROM UserAnnounceDiagram WHERE announce_id = %s", (announcement[0],))
                    join_num = cursor.fetchone()[0]
                    cursor.execute("UPDATE BoardList SET join_num = %s WHERE idBoardList = %s", (join_num, announcement[0]))
                    db.commit()
                cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
                announcements = cursor.fetchall()
                db.commit()
                response = {
                    "action": "refresh_announcement",
                    "status": "success",
                    "announcements": {
                        announcement[0]: {
                            "headline": announcement[1],
                            "college": announcement[2],
                            "deadline": announcement[3],
                            "join_num": announcement[4],
                            "proposer_name": announcement[5],
                            "type": announcement[6]
                        } for announcement in announcements
                    }
                }
                send_message(conn, response)
                
            elif action == "refresh_my_announcement":
                user_id = data.get("user_id")
                cursor.execute("""
                    SELECT b.idBoardList, b.headline, b.college, b.deadline, b.join_num, b.proposer_name, b.type 
                    FROM BoardList b
                    JOIN UserAnnounceDiagram uad ON b.idBoardList = uad.announce_id
                    WHERE uad.user_id = %s
                """, (user_id,))
                announcements_data = cursor.fetchall()
                db.commit()
                response = {
                    "action": "refresh_my_announcement",
                    "status": "success",
                    "my_announcements": {
                        announcement[0]: {
                            "headline": announcement[1],
                            "college": announcement[2],
                            "deadline": announcement[3],
                            "join_num": announcement[4],
                            "proposer_name": announcement[5],
                            "type": announcement[6]
                        } for announcement in announcements_data
                    }
                }
                send_message(conn, response)
            
            elif action == "follow_announcement":
                user_id = data.get("user_id")
                announcement_id = data.get("announcement_id")
                try:
                    cursor.execute("INSERT INTO UserAnnounceDiagram (user_id, announce_id) VALUES (%s, %s)", (user_id, announcement_id))
                    db.commit()
                    response = {"action": "follow_announcement", "status": "success", "message": "加入成功"}
                except mysql.connector.errors.IntegrityError:
                    response = {"action": "follow_announcement", "status": "fail", "message": "加入失败"}
                    db.rollback()
                send_message(conn, response)
                
            elif action == "disfollow_announcement":
                user_id = data.get("user_id")
                announcement_id = data.get("announcement_id")
                try:
                    cursor.execute("DELETE FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
                    db.commit()
                    response = {"action": "disfollow_announcement", "status": "success", "message": "退出成功"}
                except mysql.connector.errors.IntegrityError:
                    response = {"action": "disfollow_announcement", "status": "fail", "message": "退出失败"}
                    db.rollback()
                send_message(conn, response)
            
            elif action == "submit_announcement":
                title = data.get("title")
                college = data.get("college")
                user_id = data.get("user_id")
                user_name = data.get("user_name")
                announcement_type = data.get("type")
                deadline = data.get("deadline")
                content = data.get("content")
                try:
                    cursor.execute("INSERT INTO BoardList (headline, college, proposer_id, proposer_name, type, deadline, join_num, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (title, college, user_id, user_name, announcement_type, deadline, 0, content.strip()))
                    db.commit()
                    response = {"action": "submit_announcement", "status": "success", "message": "发布成功"}
                except mysql.connector.errors.IntegrityError:
                    response = {"action": "submit_announcement", "status": "fail", "message": "发布失败"}
                    db.rollback()
                send_message(conn, response)
                
            elif action == "show_user_details":
                sender_id = data.get("sender_id")
                chat_id = data.get("chat_id")
                cursor.execute("SELECT username, college, email, is_admin, bio FROM UserInfo WHERE idUserInfo = %s", (sender_id,))
                result = cursor.fetchone()
                db.commit()
                if result:
                    username, college, email, is_admin, bio = result
                    response = {
                        "action": "show_user_details",
                        "status": "success",
                        "sender_id": sender_id,
                        "chat_id": chat_id,
                        "username": username,
                        "college": college,
                        "email": email,
                        "is_admin": is_admin,
                        "bio": bio
                    }
                else:
                    response = {"action": "show_user_details", "status": "fail", "message": "获取用户信息失败"}
                send_message(conn, response)
                
            elif action == "recommend_announcements":
                user_id = data.get("user_id")
                recommended_announcements = recommend_announcements(user_id)
                response = {
                    "action": "recommend_announcements",
                    "status": "success",
                    "recommended_announcements": recommended_announcements
                }
                send_message(conn, response)
            # 其他操作如注册、关注等可在此扩展

    except Exception as e:
        print(f"错误: {e}")
    # finally:
    #     conn.close()
    #     # 清理用户
    #     for uid, connection in clients.items():
    #         if connection == conn:
    #             del clients[uid]
    #             break
    #     print(f"{addr} 连接断开")

def send_message(conn, message):
    msg = json.dumps(message, cls=DateTimeEncoder).encode()
    msg_length = len(msg).to_bytes(4, byteorder='big')
    conn.sendall(msg_length + msg)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"服务器启动，监听 {HOST}:{PORT}")
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        server.close()
        cursor.close()
        db.close()
        
def recommend_announcements(user_id):
    # 获取所有公告
    cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
    announcements = cursor.fetchall()
    db.commit()

    # 获取用户参与的公告
    cursor.execute("SELECT announce_id FROM UserAnnounceDiagram WHERE user_id = %s", (user_id,))
    user_announcements = [row[0] for row in cursor.fetchall()]
    db.commit()

    # 构建用户-项目矩阵
    user_item_matrix = {}
    cursor.execute("SELECT user_id, announce_id FROM UserAnnounceDiagram")
    for row in cursor.fetchall():
        user_id_matrix, announce_id = row
        if user_id_matrix not in user_item_matrix:
            user_item_matrix[user_id_matrix] = set()
        user_item_matrix[user_id_matrix].add(announce_id)
    db.commit()

    # 计算用户相似度（余弦相似度）
    def cosine_similarity(u, v):
        common_announcements = user_item_matrix[u].intersection(user_item_matrix[v])
        if not common_announcements:
            return 0
        numerator = len(common_announcements)
        denominator = (len(user_item_matrix[u]) * len(user_item_matrix[v])) ** 0.5
        return numerator / denominator

    # 找到与当前用户最相似的 k 个用户
    k = 5
    similar_users = []
    for other_user in user_item_matrix:
        if other_user != user_id:
            similarity = cosine_similarity(user_id, other_user)
            if similarity > 0:  # 过滤掉相似度为 0 的用户
                similar_users.append((other_user, similarity))
    similar_users.sort(key=lambda x: x[1], reverse=True)
    similar_users = similar_users[:k]

    # 计算推荐评分
    recommendation_scores = {}
    for announcement in announcements:
        announcement_id = announcement[0]
        join_num = announcement[4]  # 参与人数
        if announcement_id not in user_announcements:
            score = 0
            for other_user, similarity in similar_users:
                if announcement_id in user_item_matrix[other_user]:
                    score += similarity
            # 加入参与人数作为权重
            score *= (1 + join_num * 0.1)  # 参与人数越多，权重越高
            recommendation_scores[announcement_id] = score

    # 过滤掉评分为 0 的公告
    recommendation_scores = {announcement_id: score for announcement_id, score in recommendation_scores.items() if score > 0}

    # 按推荐评分排序
    recommended_announcements = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
    recommended_announcements = [announcement[0] for announcement in recommended_announcements]

    # 返回推荐的公告列表
    return recommended_announcements

if __name__ == "__main__":
    start_server()
