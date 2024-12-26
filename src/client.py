import webbrowser
import atexit
import requests 
import threading  
import queue
import json
import socket  # 用于创建网络通信的socket
import threading  # 用于创建和管理线程
import tkinter as tk  # 用于创建GUI
from tkinter import messagebox  # 用于显示消息框
import ctypes  # 用于调用Windows API函数
import shelve  # 用于创建简单的持久化数据库
import pickle  # 用于序列化和反序列化Python对象
import os  # 用于操作系统功能，如文件路径操作
import appdirs  # 用于获取应用程序数据目录的库
import time  # 用于时间相关的功能
import mysql.connector  # 用于连接MySQL数据库
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# 全局变量用于存储socket客户端对象和连接状态
client_socket = None
receive_thread = None
connected = False

current_user_id = None
current_username = None

import tkinter as tk
import time


class LoginGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("登录")
        self.master.geometry("300x400")
        self.register_window = None
        
        # 用户名/邮箱标签和输入框
        self.username_label = tk.Label(self.master, text="用户名/邮箱:")
        self.username_label.pack(pady=10)
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack(pady=5)
        
        # 密码标签和输入框
        self.password_label = tk.Label(self.master, text="密码:")
        self.password_label.pack(pady=10)
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack(pady=5)
        
        # 登录按钮
        self.login_button = tk.Button(self.master, text="登录", command=self.login)
        self.login_button.pack(pady=10)
        
        # 注册按钮
        self.register_button = tk.Button(self.master, text="注册", command=self.register)
        self.register_button.pack(pady=10)
        
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.master)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
        
    def login(self):
        # 登录的逻辑
        username_or_email = self.username_entry.get()
        password = self.password_entry.get()
        cursor.execute("SELECT * FROM UserInfo WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        user = cursor.fetchone()
        if user:
            if user[2] == password:  # Assuming the password is the third field in the UserInfo table
                self.show_temporary_message("登录成功", "登录成功")
                global is_login, user_id, user_name
                is_login = True
                user_id = user[0]
                user_name = user[1]
                self.master.withdraw()
                board_window = ttk.Window()
                style = ttk.Style()
                style.theme_use('')
                board = BoardGUI(board_window, style)
            else:
                self.show_temporary_message("登录失败", "密码错误")
        else:
            self.show_temporary_message("登录失败", "用户不存在")
            self.register()

    # Try to login use server
    # def login(self):
    #     username_or_email = self.username_entry.get()
    #     password = self.password_entry.get()

    #     # Prepare login data
    #     login_data = {
    #         "action": "login",
    #         "username": username_or_email,
    #         "password": password
    #     }

    #     try:
    #         # Send login data to the server
    #         message = json.dumps(login_data)
    #         client_socket.send(len(message).to_bytes(4, byteorder='big'))  # Send message length
    #         client_socket.send(message.encode())  # Send message data

    #         # Wait for the server response
    #         response_length_data = client_socket.recv(4)
    #         if not response_length_data:
    #             raise Exception("服务器未响应")
    #         response_length = int.from_bytes(response_length_data, byteorder='big')
    #         response_data = client_socket.recv(response_length).decode()
    #         response = json.loads(response_data)

    #         # Handle server response
    #         status = response.get("status")
    #         if status == "success":
    #             global is_login, user_id, user_name
    #             is_login = True
    #             user_id = response.get("user_id")
    #             user_name = self.username_entry.get()  # Save username for reference
    #             self.show_temporary_message("登录成功", "登录成功")
    #             self.master.withdraw()
    #             board_window = ttk.Window()
    #             style = ttk.Style()
    #             style.theme_use('')
    #             board = BoardGUI(board_window, style)
    #         else:
    #             error_msg = response.get("message", "登录失败")
    #             self.show_temporary_message("登录失败", error_msg)

    #     except Exception as e:
    #         print(f"登录时发生错误: {e}")
    #         messagebox.showerror("登录错误", f"登录失败: {e}")


   
            
   
    def register(self):
        # 注册的逻辑
        register_window = tk.Toplevel(self.master)
        register_window.title("注册")
        register_window.geometry("300x600")
        self.register_window = register_window
        
        # 用户名标签和输入框
        username_label = tk.Label(register_window, text="用户名*:")
        username_label.pack(pady=10)
        username_entry = tk.Entry(register_window)
        username_entry.pack(pady=5)
        
        # 密码标签和输入框
        password_label = tk.Label(register_window, text="密码*:")
        password_label.pack(pady=10)
        password_entry = tk.Entry(register_window, show="*")
        password_entry.pack(pady=5)
        
        # 确认密码标签和输入框
        confirm_password_label = tk.Label(register_window, text="确认密码*:")
        confirm_password_label.pack(pady=10)
        confirm_password_entry = tk.Entry(register_window, show="*")
        confirm_password_entry.pack(pady=5)
        
        # 显示密码复选框
        show_password_var = tk.BooleanVar()
        show_password_check = tk.Checkbutton(register_window, text="显示密码", variable=show_password_var, command=lambda: self.toggle_password_visibility(password_entry, confirm_password_entry, show_password_var))
        show_password_check.pack(pady=5)
        
        # 邮箱标签和输入框
        email_label = tk.Label(register_window, text="邮箱:")
        email_label.pack(pady=10)
        email_entry = tk.Entry(register_window)
        email_entry.pack(pady=5)
        
        # 院系标签和输入框
        college_label = tk.Label(register_window, text="院系*:")
        college_label.pack(pady=10)
        college_entry = tk.Entry(register_window)
        college_entry.pack(pady=5)
        
        # 简介标签和输入框
        bio_label = tk.Label(register_window, text="简介:")
        bio_label.pack(pady=10)
        bio_entry = tk.Entry(register_window)
        bio_entry.pack(pady=5)
        
        # 注册按钮
        submit_button = tk.Button(register_window, text="提交", command=lambda: self.submit_registration(username_entry.get(), password_entry.get(), confirm_password_entry.get(), email_entry.get(), college_entry.get(), bio_entry.get()))
        submit_button.pack(pady=10)
        
    def toggle_password_visibility(self, password_entry, confirm_password_entry, show_password_var):
        if show_password_var.get():
            password_entry.config(show="")
            confirm_password_entry.config(show="")
        else:
            password_entry.config(show="*")
            confirm_password_entry.config(show="*")
        
    def submit_registration(self, username, password, confirm_password, email, college, bio):
        if not username or not password or not college:
            self.show_temporary_message("注册失败", "用户名、密码和院系不能为空")
            return
        if password != confirm_password:
            self.show_temporary_message("注册失败", "两次输入的密码不一致")
            return
        cursor.execute("SELECT * FROM UserInfo WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            self.show_temporary_message("注册失败", "用户名已存在")
            return
        else:
            cursor.execute("INSERT INTO UserInfo (username, passwoord, email, college, bio) VALUES (%s, %s, %s, %s, %s)", (username, password, email, college, bio))
            db.commit()
            self.show_temporary_message("注册成功", "注册成功，请登录")
            self.register_window.destroy()

class Announcement:
    def __init__(self, master, announcement_id, title, department, deadline, participants, initiator, announcement_type):
        self.frame = tk.Frame(master, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        
        # 标题
        self.title_label = tk.Label(self.frame, text=title, font=('宋体', 14, 'bold'), anchor='w')
        self.title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        
        # 院系
        self.department_label = tk.Label(self.frame, text=department, font=('宋体', 12), anchor='w')
        self.department_label.grid(row=1, column=1, sticky='w', pady=2)
        
        # 截止时间
        deadline_formatted = deadline.strftime('%Y-%m-%d %H:%M')
        self.deadline_label = tk.Label(self.frame, text=f"截止时间：{deadline_formatted}", font=('宋体', 12), anchor='w', fg='black')
        self.deadline_label.grid(row=3, column=0, sticky='w', pady=2)
        
        # 参与人数
        self.participants_label = tk.Label(self.frame, text=f"参与人数: {participants}", font=('宋体', 12), anchor='w')
        self.participants_label.grid(row=2, column=1, sticky='w', pady=2)
        
        # 发起人
        self.initiator_label = tk.Label(self.frame, text=f"by {initiator}", font=('宋体', 12), anchor='w')
        self.initiator_label.grid(row=1, column=0, sticky='w', pady=2)
        
        # 公告类型
        self.announcement_type_label = tk.Label(self.frame, text=announcement_type, font=('宋体', 12), anchor='w')
        self.announcement_type_label.grid(row=2, column=0, sticky='w', pady=2)
        
        # 详情按钮
        self.details_button = tk.Button(self.frame, text="查看详情", command=lambda: self.show_details(announcement_id=announcement_id, title=title))
        self.details_button.grid(row=3, column=1, pady=2, sticky='e')
        
        self.frame.grid(sticky='nsew')
        self.announcement_id = announcement_id
        
    def show_details(self, announcement_id, title):
        details_window = tk.Toplevel(self.frame)
        details_window.title("详情")
        details_window.geometry("600x400")
        
        details_label = tk.Label(details_window, text=f"公告标题: {title}", font=('宋体', 12))
        details_label.pack(pady=20)
        
        # 从数据库中获取公告的具体内容
        cursor.execute("SELECT content FROM BoardList WHERE idBoardList = %s", (announcement_id,))
        content = cursor.fetchone()[0]
        
        content_label = tk.Label(details_window, text=f"公告内容: {content}", font=('宋体', 12), wraplength=500, justify='left')
        content_label.pack(pady=10)
        
        # 判断是否已经加入群聊
        cursor.execute("SELECT * FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
        user_announcement = cursor.fetchone()
        
        if user_announcement:
            follow_button = tk.Button(details_window, text="取消关注", command=lambda: self.disfollow_announcement(user_id, announcement_id, details_window))
            follow_button.pack(pady=10)
            chatroom_frame = tk.Frame(details_window)
            chatroom_frame.pack(fill='both', expand=True)
            chatroom = ChatroomGUI(chat_id=announcement_id)
            chatroom.master = chatroom_frame
            chatroom.master.pack(fill='both', expand=True)
            chatroom.run()
        else:
            follow_button = tk.Button(details_window, text="关注该通知", command=lambda: self.follow_announcement(user_id, announcement_id, details_window))
            follow_button.pack(pady=10)
            
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.frame)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
            
    def follow_announcement(self, user_id, announcement_id, show_details_window):
        try:
            cursor.execute("INSERT INTO UserAnnounceDiagram (user_id, announce_id) VALUES (%s, %s)", (user_id, announcement_id))
            db.commit()
            self.show_temporary_message("关注成功", "关注成功")
            show_details_window.destroy()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("关注失败", f"关注失败: {err}")
            db.rollback()
            
    def disfollow_announcement(self, user_id, announcement_id, show_details_window):
        try:
            cursor.execute("DELETE FROM UserAnnounceDiagram WHERE user_id = %s AND announce_id = %s", (user_id, announcement_id))
            db.commit()
            self.show_temporary_message("取消关注成功", "取消关注成功")
            show_details_window.destroy()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("取消关注失败", f"取消关注失败: {err}")
            db.rollback()
            

class BoardGUI:
    def __init__(self, master, style=None):
        self.master = master
        self.master.title("公告板")
        self.master.geometry("800x600")
        self.master.resizable(width=True, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 主题选择框
        theme_names = style.theme_names()
        theme_selection = ttk.Frame(self.master)
        theme_selection.pack(fill='x', pady=10)
        
        label = ttk.Label(theme_selection, text="主题:")
        label.pack(side='left', padx=5)
        
        theme_cbo = ttk.Combobox(
            master=theme_selection,
            text=style.theme.name,
            values=theme_names,
            state='readonly'
        )
        theme_cbo.pack(side='left', padx=5)
        theme_cbo.current(theme_names.index(style.theme.name))
        theme_cbo.bind("<<ComboboxSelected>>", lambda e: style.theme_use(theme_cbo.get()))
        
        # 刷新按钮
        self.refresh_button = tk.Button(theme_selection, text="刷新", command=self.show_all_announcements)
        self.refresh_button.pack(side='left', padx=5)
        
        # 发布公告按钮
        self.publish_button = tk.Button(theme_selection, text="发布公告", command=self.publish)
        self.publish_button.pack(side='left', padx=5)
        
        # 创建一个画布和滚动条
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定滚动事件
        self.canvas.bind_all('<MouseWheel>', lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        self.canvas.bind_all('<Button-4>', lambda event: self.canvas.yview_scroll(-1, "units"))  # For Linux
        self.canvas.bind_all('<Button-5>', lambda event: self.canvas.yview_scroll(1, "units"))  # For Linux
        
        # 标签页框架
        self.tab_frame = tk.Frame(self.master)
        self.tab_frame.pack(side='left', fill='y', pady=5)
        
        self.all_announcements_button = tk.Button(self.tab_frame, text="公告板", command=self.show_all_announcements)
        self.all_announcements_button.pack(side='top', expand=True, fill='x', pady=5, padx=20)
        
        self.my_announcements_button = tk.Button(self.tab_frame, text="我的", command=self.show_my_announcements)
        self.my_announcements_button.pack(side='top', expand=True, fill='x', pady=5, padx=20)
        
        self.current_tab = "all"
        self.highlight_current_tab()
        # 从数据库中获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 从 UserAnnounceDiagram 中更新 join_num
        for announcement in announcements_data:
            cursor.execute("SELECT COUNT(*) FROM UserAnnounceDiagram WHERE announce_id = %s", (announcement[0],))
            join_num = cursor.fetchone()[0]
            cursor.execute("UPDATE BoardList SET join_num = %s WHERE idBoardList = %s", (join_num, announcement[0]))
            db.commit()
        
        # 更新 join_num 后重新获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 创建公告对象列表
        self.announcements = []
        self.create_announcements(announcements_data)
        
    def create_announcements(self, announcements_data):
        def update_grid(event=None):
            width = self.master.winfo_width()
            columns = max(1, width // 400)  # 每列宽度约为400像素
            for i, announcement in enumerate(self.announcements):
                announcement.frame.grid(row=i // columns, column=i % columns, padx=10, pady=10, sticky='nsew')

        for announcement_data in announcements_data:
            announcement = Announcement(self.scrollable_frame, *announcement_data)
            self.announcements.append(announcement)

        self.master.bind('<Configure>', update_grid)
        update_grid()
    
    def refresh(self):
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        
        # 从数据库中获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 从 UserAnnounceDiagram 中更新 join_num
        for announcement in announcements_data:
            cursor.execute("SELECT COUNT(*) FROM UserAnnounceDiagram WHERE announce_id = %s", (announcement[0],))
            join_num = cursor.fetchone()[0]
            cursor.execute("UPDATE BoardList SET join_num = %s WHERE idBoardList = %s", (join_num, announcement[0]))
            db.commit()
        
        # 更新 join_num 后重新获取公告数据
        cursor.execute("SELECT idBoardList, headline, college, deadline, join_num, proposer_name, type FROM BoardList")
        announcements_data = cursor.fetchall()
        
        # 创建新的公告对象列表
        self.create_announcements(announcements_data)
        
    def show_temporary_message(self, title, message):
        # 创建一个顶级窗口
        temp_window = tk.Toplevel(self.master)
        temp_window.title(title)
        temp_window.geometry("200x100")
        
        # 错误消息标签
        message_label = tk.Label(temp_window, text=message)
        message_label.pack(pady=20)
        
        # 设置定时器，3秒后关闭窗口
        temp_window.after(1000, temp_window.destroy)
    
    def publish(self):
        # 发布公告的逻辑
        if not is_login:
            self.show_temporary_message("发布失败", "请先登录")
            return
        
        if not user_id:
            self.show_temporary_message("发布失败", "用户ID无效")
            return
        
        cursor.execute("SELECT is_admin FROM UserInfo WHERE idUserInfo = %s", (user_id,))
        is_admin = cursor.fetchone()[0]
        
        if not is_admin:
            self.show_temporary_message("发布失败", "只有管理员可以发布公告")
            return
        
        publish_window = tk.Toplevel(self.master)
        publish_window.title("发布公告")
        publish_window.geometry("400x800")
        
        # 标题标签和输入框
        title_label = tk.Label(publish_window, text="标题*:")
        title_label.pack(pady=10)
        title_entry = tk.Entry(publish_window)
        title_entry.pack(pady=5)
        
        # 院系标签和输入框
        college_label = tk.Label(publish_window, text="院系*:")
        college_label.pack(pady=10)
        college_entry = tk.Entry(publish_window)
        college_entry.pack(pady=5)
        
        # 截止时间标签和输入框
        deadline_label = tk.Label(publish_window, text="截止时间* (YYYY-MM-DD HH:MM:SS):")
        deadline_label.pack(pady=10)
        deadline_entry = tk.Entry(publish_window)
        deadline_entry.pack(pady=5)
        
        # 公告类型标签和输入框
        type_label = tk.Label(publish_window, text="公告类型*:")
        type_label.pack(pady=10)
        type_entry = tk.Entry(publish_window)
        type_entry.pack(pady=5)
        
        # 内容标签和输入框
        content_label = tk.Label(publish_window, text="内容*:")
        content_label.pack(pady=10)
        content_text = tk.Text(publish_window, height=10)
        content_text.pack(pady=5)
        
        # 提交按钮
        submit_button = tk.Button(publish_window, text="提交", command=lambda: self.submit_announcement(title_entry.get(), college_entry.get(), deadline_entry.get(), type_entry.get(), content_text.get("1.0", tk.END), publish_window))
        submit_button.pack(pady=10)
        
    def submit_announcement(self, title, college, deadline, announcement_type, content, publish_window):
        if not title or not college or not deadline or not announcement_type or not content.strip():
            self.show_temporary_message("发布失败", "所有字段均为必填项")
            return
        
        try:
            cursor.execute("INSERT INTO BoardList (headline, college, proposer_name, type, deadline, join_num, content) VALUES (%s, %s, %s, %s, %s, %s, %s)", (title, college, user_name, announcement_type, deadline, 0, content.strip()))
            db.commit()
            self.show_temporary_message("发布成功", "公告发布成功")
            publish_window.destroy()
            self.refresh()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.show_temporary_message("发布失败", f"发布失败: {err}")
            db.rollback()
    
    def on_closing(self):  
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.master.destroy()
            exit(0)
        else:
            pass
    
    def show_all_announcements(self):
        self.current_tab = "all"
        self.highlight_current_tab()
        self.refresh()
    
    def show_my_announcements(self):
        self.current_tab = "my"
        self.highlight_current_tab()
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        
        # 从数据库中获取我加入的公告数据
        cursor.execute("""
            SELECT b.idBoardList, b.headline, b.college, b.deadline, b.join_num, b.proposer_name, b.type 
            FROM BoardList b
            JOIN UserAnnounceDiagram uad ON b.idBoardList = uad.announce_id
            WHERE uad.user_id = %s
        """, (user_id,))
        announcements_data = cursor.fetchall()
        
        # 创建新的公告对象列表
        self.create_announcements(announcements_data)
    
    def highlight_current_tab(self):
        if self.current_tab == "all":
            self.all_announcements_button.config(relief="sunken", bg="lightblue")
            self.my_announcements_button.config(relief="raised", bg="SystemButtonFace")
        else:
            self.all_announcements_button.config(relief="raised", bg="SystemButtonFace")
            self.my_announcements_button.config(relief="sunken", bg="lightblue")

class ChatroomGUI:
    def __init__(self, chat_id=1):
        self.master = tk.Tk()
        # self.message_queue = queue.Queue()
        # self.master.after(100, self.process_queue)
        self.master.title("聊天室")
        self.master.geometry("800x600")
        self.master.resizable(width=False, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.user_id = 1
        self.chat_id = chat_id

        # 聊天记录框架
        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(fill='both', expand=True, pady=10)
        
        # 创建一个画布和滚动条
        self.canvas = tk.Canvas(self.chat_frame)
        self.scrollbar = tk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定滚动事件
        self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind_all('<Button-4>', self.on_mouse_wheel)  # For Linux
        self.canvas.bind_all('<Button-5>', self.on_mouse_wheel)  # For Linux

        # 消息输入框
        self.message_entry = tk.Text(self.master, font=('宋体', 12), height=3, wrap='word')
        self.message_entry.pack(fill='x', pady=10)
        
        # 发送按钮
        self.send_button = tk.Button(self.master, text="发送", command=self.send_message)
        self.send_button.pack(side='right', padx=10, pady=10)
        
        # 绑定事件以自适应输入框高度
        self.message_entry.bind('<KeyRelease>', self.adjust_textbox_height)
            
        # 绑定回车键事件到 send_message 方法
        self.master.bind('<KeyPress-Return>', self.send_message_on_enter)
        
        # 初始化最旧的消息时间戳
        self.oldest_timestamp = time.time()
        self.message_shown = []
    # def process_queue(self):
    #     while not self.message_queue.empty():
    #         func, args = self.message_queue.get()
    #         func(*args)  # Execute the function with arguments
    #     self.master.after(100, self.process_queue)

    def adjust_textbox_height(self, event=None):
        lines = int(self.message_entry.index('end-1c').split('.')[0])
        self.message_entry.config(height=max(3, lines))
        
    def on_mouse_wheel(self, event):
        if event.delta > 0 and self.canvas.yview()[0] == 0.0:
            self.refresh_older_messages()
        else:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
    def display_message(self, message, sender_id, sender_name, timestamp):
        # 创建一个消息框架
        message_frame = tk.Frame(self.scrollable_frame, bd=2, relief=tk.SUNKEN, padx=5, pady=5, width=780)
        
        # 创建一个内部框架用于纵向排列发送者和时间
        info_frame = tk.Frame(message_frame)
        info_frame.pack(side='left', fill='y', padx=5)
        
        # 显示发送者
        sender_label = tk.Label(info_frame, text=sender_name, font=('宋体', 10, 'bold'), anchor='w', fg='blue', cursor="hand2")
        sender_label.pack(fill='x')
        sender_label.bind("<Button-1>", lambda e: self.show_user_details(sender_id, sender_name))
        
        # 显示发送时间
        # time_current=time.time()

        # timestamp_float = timestamp.timestamp()

        if timestamp:
            if isinstance(timestamp, str):
                timestamp_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                timestamp_float = timestamp_obj.timestamp()
                time_diff = time.time() - timestamp_float
            elif isinstance(timestamp, datetime):
                time_diff = time.time() - timestamp.timestamp()
            elif isinstance(timestamp, float):
                time_diff = time.time() - timestamp
            if time_diff < 60:
                time_str = "刚刚"
            elif time_diff < 3600:
                time_str = f"{int(time_diff // 60)}分钟前"
            elif time_diff < 86400:
                time_str = f"{int(time_diff // 3600)}小时前"
            else:
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
        else:
            time_str = ""
        time_label = tk.Label(info_frame, text=time_str, font=('宋体', 8), anchor='w')
        time_label.pack(fill='x')
        
        # 显示消息内容
        message_label = tk.Label(message_frame, text=message, font=('宋体', 12), wraplength=700, justify='left')
        message_label.pack(side='left', fill='x', expand=True)
        
        if sender_id == self.user_id:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='e')
            message_frame.config(highlightbackground='blue', highlightthickness=2)
            info_frame.pack(side='right', fill='y', padx=5)
            message_label.config(justify='right')
            message_label.pack(side='right')

        else:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='w')
            message_frame.config(highlightbackground='gray', highlightthickness=1)
            info_frame.pack(side='left', fill='y', padx=5)
            message_label.config(justify='left')
            message_label.pack(side='left')
        
        # 滚动到最新消息
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def handle_server_message(self, message):
        print(f"Running on thread: {threading.current_thread().name}")
        action = message.get("action")
        if action == "receive_message":
            print("Message will be displayed soon.")
            sender_id = message.get("sender_id")
            content = message.get("content")
            timestamp = message.get("timestamp")
            sender_name = message.get("sender_name")

            # Schedule GUI update on the main thread
            if self.master:
                self.master.after(0, lambda: self.display_message(content, sender_id, sender_name, timestamp))

        # elif action == "login":
        #     status = message.get("status")
        #     if status == "success":
        #         global current_user_id, current_username
        #         current_user_id = message.get("user_id")
        #         is_admin = message.get("is_admin")
        #         current_username = app.login_gui.username_entry.get()
        #         #app.login_success()
        #     else:
        #         error_msg = message.get("message")
        #         #app.login_gui.show_temporary_message("登录失败", error_msg)


    def receive_messages(self):
        global connected
        try:
            while connected:
                # 接收消息长度
                print("Message received from server.")
                msg_length_data = client_socket.recv(4)
                if not msg_length_data:
                    break
                msg_length = int.from_bytes(msg_length_data, byteorder='big')
                # 接收实际消息
                msg_data = client_socket.recv(msg_length).decode()
                message = json.loads(msg_data)
                self.handle_server_message(message)
        except Exception as e:
            print(f"接收消息错误: {e}")
        finally:
            client_socket.close()
            connected = False
            print("与服务器的连接已关闭")            
    def connect_to_server(self):
        global client_socket, connected
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            connected = True
            print("成功连接到服务器")
            
            # Start the receive thread after GUI is initialized
            self.master.after(0, self.start_receive_thread)
        except Exception as e:
            print(f"无法连接到服务器: {e}")
            messagebox.showerror("连接错误", f"无法连接到服务器: {e}")

    def start_receive_thread(self):
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()

        
    def show_user_details(self, sender_id, sender_name):
        # 显示用户详情的逻辑
        cursor.execute("SELECT username, college, email, is_admin, bio FROM UserInfo WHERE idUserInfo = %s", (sender_id,))
        user_details = cursor.fetchone()
        
        if user_details:
            username, college, email, is_admin, bio = user_details
            
            user_details_window = tk.Toplevel(self.master)
            user_details_window.title("用户详情")
            user_details_window.geometry("400x300")
            
            # 创建一个框架用于放置用户信息
            details_frame = tk.Frame(user_details_window, bd=2, relief=tk.RIDGE, padx=10, pady=10)
            details_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # 用户名和管理员标签
            username_frame = tk.Frame(details_frame)
            username_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            username_title = tk.Label(username_frame, text=f"{username}", font=('宋体', 14, 'bold'), fg='black')
            username_title.pack(side='left')
            if is_admin:
                admin_label = tk.Label(username_frame, text="管理员", font=('宋体', 10), fg='red', bg='lightblue')
                admin_label.pack(side='left', padx=5)
            
            # 院系
            college_label = tk.Label(details_frame, text=f"{college}", font=('宋体', 12), anchor='w')
            college_label.grid(row=1, column=0, sticky='w', pady=5)
            
            # 邮箱
            email_label = tk.Label(details_frame, text=f"{email}", font=('宋体', 12), anchor='w')
            email_label.grid(row=1, column=1, sticky='w', pady=5)
            
            # 简介
            bio_label = tk.Label(details_frame, text=f"简介: {bio}", font=('宋体', 12), wraplength=350, justify='left')
            bio_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)

    def send_message(self):
    # 发送消息的逻辑
        content = self.message_entry.get("1.0", tk.END).strip()
        current_user_id=self.user_id
        if not connected and content and current_user_id:
            self.connect_to_server()
            message = {
                "action": "send_message",
                "sender_id": current_user_id,
                "chat_id": self.chat_id,
                "sender_name":"我",
                "content": content
            }
            self.send_message_to_server(message)
        elif connected and content and current_user_id:
            message = {
                "action": "send_message",
                "sender_id": current_user_id,
                "chat_id": self.chat_id,
                "sender_name":"我",
                "content": content
            }
            self.send_message_to_server(message)
            #timestamp = datetime.now()
            #self.display_message(content=content, sender_id=current_user_id, sender_name=current_username, timestamp=timestamp)
            self.message_entry.delete("1.0", tk.END)
        else:
            print("用户或内容不存在，未发送消息到服务器")
    
    def send_message_to_server(self,message):
        try:
            msg = json.dumps(message).encode()
            msg_length = len(msg).to_bytes(4, byteorder='big')
            print("Message sent to server.")
            client_socket.sendall(msg_length + msg)
        except Exception as e:
            print(f"发送消息错误: {e}")
            messagebox.showerror("发送错误", f"发送消息失败: {e}")
            raise  # Reraise the exception if needed
    def notify_disconnection(self, error_message):
        messagebox.showerror("连接错误", f"连接中断: {error_message}")

    def close_connection(self):
        print("清理资源并更新GUI")
        # Any cleanup code, such as disabling buttons

    
    def send_message_on_enter(self, event):
        # 调用发送消息方法，忽略事件对象
        self.send_message()
    
    def run(self):
        self.load_recent_messages()
        self.master.mainloop()

    def load_recent_messages(self):
        # 获取最近一天的聊天记录
        cursor.execute("""
            SELECT sender_id, sender_name, content, timestamp 
            FROM ChatMessages 
            WHERE idBoardList = %s AND timestamp >= NOW() - INTERVAL 1 DAY 
            ORDER BY timestamp DESC
        """, (self.chat_id,))
        messages = cursor.fetchall()

        for message in reversed(messages):
            sender_id, sender_name, content, timestamp = message
            self.display_message(sender_id=sender_id, sender_name=sender_name, message=content, timestamp=timestamp)
            
        self.oldest_timestamp = messages[-1][3] if messages else time.time()
        print("已加载最近的消息")
        print("最旧的消息时间戳:", self.oldest_timestamp)
        self.message_shown.extend(messages)

    def refresh_older_messages(self):
        # 获取更早的聊天记录
        cursor.execute("""
            SELECT sender_id, sender_name, content, timestamp 
            FROM ChatMessages 
            WHERE idBoardList = %s AND timestamp < %s 
            ORDER BY timestamp DESC 
            LIMIT 20
        """, (self.chat_id, self.oldest_timestamp))
        messages = cursor.fetchall()
        self.message_shown.extend(messages)
        if messages:
            self.oldest_timestamp = messages[-1][3]
            current_scroll_position = self.canvas.yview()[0]
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            for message in reversed(self.message_shown):
                sender_id, sender_name, content, timestamp = message
                self.display_message(sender_id=sender_id, sender_name=sender_name, message=content, timestamp=timestamp)
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(current_scroll_position)
        
        print("已加载更早的消息")
        print("最旧的消息时间戳:", self.oldest_timestamp)
        return bool(messages)
    
# 主程序
if __name__ == "__main__":
    try:
        # 连接到数据库
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="pjy530150",
            database="COMM"
        )
        cursor = db.cursor()
        print("数据库连接成功！")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("数据库连接错误", f"无法连接到数据库: {err}")
        exit(1)
    
    # 创建主窗口，显示公告板，可更换主题
    is_login = False
    user_id = None
    user_name = None

    
    root = ttk.Window()
    style = ttk.Style()
    style.theme_use('')
    
    app = LoginGUI(master=root)
    root.mainloop()
    
    # 关闭数据库连接
    cursor.close()
    db.close()
