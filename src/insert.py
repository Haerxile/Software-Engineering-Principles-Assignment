
import mysql.connector  # 用于连接MySQL数据库
import atexit
from tkinter import messagebox


if __name__ == "__main__":
    try:
        # 连接到数据库
        db = mysql.connector.connect(
            host="localhost",
            user="Haerxile",
            password="200518",
            database="COMM"
        )
        cursor = db.cursor()
        print("数据库连接成功！")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("数据库连接错误", f"无法连接到数据库: {err}")
        exit(1)
    
    # 插入测试数据

    test_data = [
        (1, "计算机科学讲座", "计算机学院", "Haerxile", "讲座", "2023-11-30 18:00:00", 50, "欢迎参加计算机科学讲座，了解最新的技术趋势和研究成果。"),
        (2, "英语角活动", "外国语学院", "Alice", "活动", "2023-12-01 15:00:00", 30, "加入我们的英语角活动，提升你的英语口语能力。"),
        (3, "数学竞赛报名", "数学学院", "Bob", "竞赛", "2023-12-05 23:59:59", 100, "数学竞赛报名开始了，展示你的数学才华，赢取丰厚奖品。"),
        (4, "物理实验室开放日", "物理学院", "Charlie", "开放日", "2023-12-10 10:00:00", 20, "物理实验室开放日，欢迎大家前来参观和体验最新的实验设备。"),
        (5, "化学实验安全培训", "化学学院", "David", "培训", "2023-12-15 14:00:00", 40, "化学实验安全培训，确保实验操作的安全性和规范性。"),
        (6, "生物科技创新大赛", "生物学院", "Eve", "竞赛", "2023-12-20 17:00:00", 60, "生物科技创新大赛，展示你的创新能力，赢取大奖。"),
        (7, "地理野外考察", "地理学院", "Frank", "考察", "2023-12-25 08:00:00", 25, "地理野外考察活动，亲身体验自然地理现象，提升实践能力。"),
        (8, "历史文化讲座", "历史学院", "Grace", "讲座", "2023-12-30 19:00:00", 35, "历史文化讲座，了解中华文明的悠久历史和文化底蕴。"),
        (9, "政治理论研讨会", "政治学院", "Heidi", "研讨会", "2024-01-05 16:00:00", 45, "政治理论研讨会，深入学习和探讨马克思主义理论和中国特色社会主义。"),
        (10, "心理健康讲座", "心理学院", "Ivan", "讲座", "2024-01-10 20:00:00", 55, "心理健康讲座，关注心理健康问题，提升心理素质。"),
        (11, "体育锻炼活动", "体育学院", "Judy", "活动", "2024-01-15 07:00:00", 65, "体育锻炼活动，锻炼身体，增强体质。"),
        (12, "音乐会演出", "音乐学院", "Mallory", "演出", "2024-01-20 21:00:00", 75, "音乐会演出，欣赏美妙的音乐，感受音乐的魅力。"),
        (13, "美术展览", "美术学院", "Niaj", "展览", "2024-01-25 13:00:00", 85, "美术展览，欣赏艺术作品，感受艺术的魅力。"),
        (14, "舞蹈表演", "舞蹈学院", "Olivia", "表演", "2024-01-30 22:00:00", 95, "舞蹈表演，富有激情和活力的舞蹈表演，绝对可以让你沉浸其中。"),
        (15, "戏剧演出", "戏剧学院", "Peggy", "演出", "2024-02-05 12:00:00", 105, "戏剧演出，精彩纷呈的戏剧表演，让你感受戏剧的魅力。"),
        (16, "电影放映", "电影学院", "Sybil", "放映", "2024-02-10 23:00:00", 115, "电影放映，欣赏经典电影，感受电影的魅力。")
    ]
    test_massage = [
        (1, 1, 1, "Haerxile", "大家好，欢迎参加计算机科学讲座！", "2023-11-01 10:00:00"),
        (2, 1, 2, "Alice", "很高兴能参加这个讲座，期待学习新知识。", "2023-11-01 10:05:00"),
        (3, 1, 3, "Bob", "计算机科学是一个非常有趣的领域。", "2023-11-01 10:10:00"),
        (4, 1, 4, "Charlie", "希望能在讲座中学到更多关于编程的知识。", "2023-11-01 10:15:00"),
        (5, 1, 5, "David", "我对人工智能特别感兴趣。", "2023-11-01 10:20:00"),
        (6, 1, 6, "Eve", "讲座的内容非常丰富，受益匪浅。", "2023-11-01 10:25:00"),
        (7, 1, 7, "Frank", "希望能有更多这样的讲座。", "2023-11-01 10:30:00"),
        (8, 1, 8, "Grace", "讲座的讲师非常专业。", "2023-11-01 10:35:00"),
        (9, 1, 9, "Heidi", "我对计算机网络有很多疑问，希望能在讲座中找到答案。", "2023-11-01 10:40:00"),
        (10, 1, 10, "Ivan", "讲座的互动环节非常有趣。", "2023-11-01 10:45:00"),
        (11, 1, 11, "Judy", "讲座的内容非常实用。", "2023-11-01 10:50:00"),
        (12, 1, 12, "Mallory", "希望能有更多关于编程语言的讲解。", "2023-11-01 10:55:00"),
        (13, 1, 13, "Niaj", "讲座的案例分析非常详细。", "2023-11-01 11:00:00"),
        (14, 1, 14, "Olivia", "讲座的PPT制作得非常精美。", "2023-11-01 11:05:00"),
        (15, 1, 15, "Peggy", "讲座的内容非常前沿。", "2023-11-01 11:10:00"),
        (16, 1, 16, "Sybil", "希望能有更多关于计算机安全的讲解。", "2023-11-01 11:15:00"),
        (17, 1, 1, "Haerxile", "讲座结束，感谢大家的参与！", "2024-12-22 0:20:00"),
        (18, 2, 1, "Haerxile", "大家好，欢迎参加英语角活动！", "2023-12-01 15:00:00"),
    ]
    test_user = [
        (1, "Haerxile", "123456", "工学院", "admin@outlook.com", 1, "I am a student of College of Engeering, and I love programming.", "./pic1.png"),
        (2, "Alice", "123456", "文学院", "alice@pku.edu.cn", 0, "我是文学院的学生，喜欢文学。", "./pic2.png"),
        (3, "Bob", "123456", "理学院", "bob@edu.cn", 0, "I am a student of College of Science, and I love math.", "./pic3.png"),
        (4, "Charlie", "123456", "法学院", "charlie@pku.edu.cn", 0, "我是法学院的学生，喜欢法律。", "./pic4.png"),
        (5, "David", "123456", "信息学院", "david@pku.edu.cn", 0, "我是信息学院的学生，喜欢计算机科学。", "./pic5.png"),
        (6, "Eve", "123456", "经济学院", "eve@pku.edu.cn", 0, "我是经济学院的学生，喜欢经济学。", "./pic6.png"),
        (7, "Frank", "123456", "管理学院", "frank@pku.edu.cn", 0, "我是管理学院的学生，喜欢管理学。", "./pic7.png"),
        (8, "Grace", "123456", "教育学院", "grace@pku.edu.cn", 0, "我是教育学院的学生，喜欢教育学。", "./pic8.png"),
        (9, "Heidi", "123456", "艺术学院", "heidi@pku.edu.cn", 0, "我是艺术学院的学生，喜欢艺术。", "./pic9.png"),
        (10, "Ivan", "123456", "体育学院", "ivan@pku.edu.cn", 0, "我是体育学院的学生，喜欢体育。", "./pic10.png"),
        (11, "Judy", "123456", "音乐学院", "judy@pku.edu.cn", 0, "我是音乐学院的学生，喜欢音乐。", "./pic11.png"),
        (12, "Mallory", "123456", "医学院", "mallory@pku.edu.cn", 0, "我是医学院的学生，喜欢医学。", "./pic12.png"),
        (13, "Niaj", "123456", "环境学院", "niaj@pku.edu.cn", 0, "我是环境学院的学生，喜欢环境科学。", "./pic13.png"),
        (14, "Olivia", "123456", "新闻学院", "olivia@pku.edu.cn", 0, "我是新闻学院的学生，喜欢新闻学。", "./pic14.png"),
        (15, "Peggy", "123456", "哲学院", "peggy@pku.edu.cn", 0, "我是哲学院的学生，喜欢哲学。", "./pic15.png"),
        (16, "Sybil", "123456", "心理学院", "sybil@pku.edu.cn", 0, "我是心理学院的学生，喜欢心理学。", "./pic16.png")
    ]
    test_Diagram = [(i, (i-1)//16+1, (i-1)%16+1) for i in range(1, 129)]

    # 插入数据前先清空表
    cursor.execute("DELETE FROM UserAnnounceDiagram")
    cursor.execute("DELETE FROM BoardList")
    cursor.execute("DELETE FROM ChatMessages")
    cursor.execute("DELETE FROM UserInfo")
    db.commit()

    # 插入测试数据
    for data in test_data:
        cursor.execute("INSERT INTO BoardList (idBoardList, headline, college, proposer_name, type, deadline, join_num, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", data)
    for message in test_massage:
        cursor.execute("INSERT INTO ChatMessages (idChatMessages, idBoardList, sender_id, sender_name, content, timestamp) VALUES (%s, %s, %s, %s, %s, %s)", message)
    for user in test_user:
        cursor.execute("INSERT INTO UserInfo (idUserInfo, username, password, college, email, is_admin, bio, profile_pictrue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", user)
    for diagram in test_Diagram:
        cursor.execute("INSERT INTO UserAnnounceDiagram (idUserAnnounceDiagram, user_id, announce_id) VALUES (%s, %s, %s)", diagram)
    db.commit()

#    # 删除测试数据
#    def delete_test_data():
#        cursor.execute("DELETE FROM BoardList WHERE idBoardList IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)")
#        cursor.execute("DELETE FROM ChatMessages WHERE idChatMessages IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18)")
#        cursor.execute("DELETE FROM UserInfo WHERE idUserInfo IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)")
#        cursor.execute("DELETE FROM UserAnnounceDiagram WHERE idUserAnnounceDiagram IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)")
#        db.commit()
#
#    # 在程序结束时删除测试数据
#    atexit.register(delete_test_data)
    
    print("数据插入成功！")
