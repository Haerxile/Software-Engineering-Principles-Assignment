import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# import mysql.connector
import time
import atexit

import queue

# 添加消息队列
message_queue = queue.Queue()
root = None

# 其他导入保持不变

# 全局变量用于存储socket客户端对象和连接状态
global client_socket, receive_thread, connected
client_socket = None
receive_thread = None
connected = False

# 用户当前窗口信息
global active_chatrooms, announcement_list, board_ui, login_ui
active_chatrooms = {}
announcement_list = {}
board_ui = None
login_ui = None

# 用户登录信息
global current_user_is_login, current_user_id, current_username, cuurent_user_is_admin
current_user_is_login = False
current_user_id = None
current_username = None
cuurent_user_is_admin = False

def connect_to_server():
    global client_socket, connected
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 10086))  # 服务器地址和端口
        connected = True
        print("成功连接到服务器")
        # 启动接收线程
        receive_thread = threading.Thread(target=receive_messages, daemon=True)
        receive_thread.start()
        
        # 启动消息处理
        root.after(100, process_message_queue)
    except Exception as e:
        print(f"无法连接到服务器: {e}")
        messagebox.showerror("连接错误", f"无法连接到服务器: {e}")
        time.sleep(5)
        connect_to_server()

def receive_messages():
    global connected
    try:
        while connected:
            # 接收消息长度
            msg_length_data = client_socket.recv(4)
            if not msg_length_data:
                break
            msg_length = int.from_bytes(msg_length_data, byteorder='big')
            # 接收实际消息
            msg_data = client_socket.recv(msg_length).decode()
            message = json.loads(msg_data)
            # 将消息放入队列而不是直接处理
            message_queue.put(message)
    except Exception as e:
        print(f"接收消息错误: {e}")
    # finally:
    #     client_socket.close()
    #     connected = False
    #     print("与服务器的连接已关闭")

def process_message_queue():
    try:
        while True:
            # 非阻塞方式检查队列
            try:
                message = message_queue.get_nowait()
                handle_server_message(message)
            except queue.Empty:
                break
    except Exception as e:
        print(f"处理消息队列错误: {e}")
    # 无论如何，都要在下一个周期调度   
    if connected:
        root.after(100, process_message_queue)

def handle_server_message(message):
    print(f"收到消息: {json.dumps(message, ensure_ascii=False)}")
    action = message.get("action")
    if action == "receive_message":
        status = message.get("status")
        if status == "success":
            sender_id = message.get("sender_id")
            sender_name = message.get("sender_name")
            chat_id = message.get("chat_id")
            content = message.get("content")
            timestamp = message.get("timestamp")
            print(f"处理消息: sender_id={sender_id}, sender_name={sender_name}, content={content}, timestamp={timestamp}")
            # 使用 after 方法将 UI 更新操作调度到主线程
            if chat_id in active_chatrooms:
                print(f"在聊天室中显示消息: {content}")
                active_chatrooms[chat_id].master.after(0, lambda: active_chatrooms[chat_id].display_message(content, sender_id, sender_name, timestamp))
        else:
            error_msg = message.get("message")
            print(f"收发消息失败: {error_msg}")
    elif action == "load_recent_messages":
        status = message.get("status")
        if status == "success":
            chat_id = message.get("chat_id")
            messages = message.get("messages")
            print(f"处理最近消息: chat_id={chat_id}, messages={messages}")
            if chat_id in active_chatrooms:
                active_chatrooms[chat_id].master.after(0, lambda: active_chatrooms[chat_id].display_messages_upper(messages))
        else:
            error_msg = message.get("message")
            print(f"加载最近消息失败: {error_msg}")
    elif action == "refresh_older_messages":
        status = message.get("status")
        if status == "success":
            chat_id = message.get("chat_id")
            messages = message.get("messages")
            print(f"处理更早消息: chat_id={chat_id}, messages={messages}")
            if chat_id in active_chatrooms:
                active_chatrooms[chat_id].master.after(0, lambda: active_chatrooms[chat_id].display_messages_upper(messages))
        else:
            error_msg = message.get("message")
            print(f"加载更早消息失败: {error_msg}")
    elif action == "login":
        status = message.get("status")
        print(f"处理登录: status={status}")
        if status == "success":
            global current_user_id, current_username, cuurent_user_is_admin, login_ui
            current_user_id = message.get("user_id")
            cuurent_user_is_admin = message.get("is_admin")
            current_username = message.get("username")
            print(f"登录成功: user_id={current_user_id}, username={current_username}, is_admin={cuurent_user_is_admin}")
            login_ui.master.after(0, login_ui.login_success)
        else:
            error_msg = message.get("message")
            print(f"登录失败: {error_msg}")
            login_ui.master.after(0, lambda: login_ui.show_temporary_message("登录失败", error_msg))
            if status == "no_user":
                # 未找到用户，提示用户注册
                login_ui.master.after(0, login_ui.register)
    elif action == "register":
        status = message.get("status")
        print(f"处理注册: status={status}")
        if status == "success":
            print("注册成功")
            login_ui.master.after(0, login_ui.register_success)
        else:
            error_msg = message.get("message")
            print(f"注册失败: {error_msg}")
            login_ui.master.after(0, lambda: login_ui.show_temporary_message("注册失败", error_msg))
    elif action == "show_announce_detail":
        status = message.get("status")
        print(f"处理公告详情: status={status}")
        if status == "success":
            announcement_id = message.get("announcement_id")
            title = message.get("title")
            content = message.get("content")
            is_add_in = message.get("is_add_in")
            print(f"公告详情: announcement_id={announcement_id}, title={title}, content={content}, is_add_in={is_add_in}")
            global board_ui
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_detail_content(announcement_id, title, content, is_add_in))
            else:
                print("公告详情窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"获取公告详情失败: {error_msg}")
            messagebox.showerror("获取公告详情失败", error_msg)
            
    elif action == "refresh_announcement":
        status = message.get("status")
        print(f"处理刷新公告: status={status}")
        if status == "success":
            announcements_data = message.get("announcements")
            print(f"公告数据: {announcements_data}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.refresh(announcements_data))
            else:
                print("公告板窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"刷新公告失败: {error_msg}")
            messagebox.showerror("刷新公告失败", error_msg)
    elif action == "refresh_my_announcement":
        status = message.get("status")
        print(f"处理刷新我的公告: status={status}")
        if status == "success":
            announcements_data = message.get("my_announcements")
            print(f"我的公告数据: {announcements_data}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.refresh(announcements_data))
            else:
                print("公告板窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"刷新我的公告失败: {error_msg}")
            messagebox.showerror("刷新我的公告失败", error_msg)
    elif action == "follow_announcement":
        status = message.get("status")
        print(f"处理关注公告: status={status}")
        if status == "success":
            announcement_id = message.get("announcement_id")
            print(f"关注公告成功: announcement_id={announcement_id}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_all_announcements())
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("关注公告成功", "关注公告成功"))
            else:
                print("公告板窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"关注公告失败: {error_msg}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("关注公告失败", error_msg))
            else:
                print("公告板窗口不存在")
    elif action == "disfollow_announcement":
        status = message.get("status")
        print(f"处理取消关注公告: status={status}")
        if status == "success":
            announcement_id = message.get("announcement_id")
            print(f"取消关注公告成功: announcement_id={announcement_id}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_all_announcements())
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("取消关注公告成功", "取消关注公告成功"))
            else:
                print("公告板窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"取消关注公告失败: {error_msg}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("取消关注公告失败", error_msg))
            else:
                print("公告板窗口不存在")
    elif action == "submit_announcement":
        status = message.get("status")
        message = message.get("message")
        print(f"处理提交公告: status={status}")
        if status == "success":
            print("提交公告成功")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_all_announcements())
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("提交公告成功", message))
                board_ui.publish_window.destroy()
            else:
                print("公告板窗口不存在")
        else:
            print(f"提交公告失败: {error_msg}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("提交公告失败", message))
            else:
                print("公告板窗口不存在")
    elif action == "show_user_details":
        status = message.get("status")
        print(f"处理用户详情: status={status}")
        if status == "success":
            sender_id = message.get("sender_id")
            username = message.get("username")
            email = message.get("email")
            college = message.get("college")
            bio = message.get("bio")
            chat_id = message.get("chat_id")
            is_admin = message.get("is_admin")
            print(f"用户详情: sender_id={sender_id}, username={username}, email={email}, college={college}, bio={bio}")
            if chat_id in active_chatrooms:
                active_chatrooms[chat_id].master.after(0, lambda: active_chatrooms[chat_id].show_user_details(sender_id, username, email, college, is_admin, bio))
            else:
                print("聊天室窗口不存在")
        else:
            error_msg = message.get("message")
            print(f"获取用户详情失败: {error_msg}")
            if board_ui:
                board_ui.master.after(0, lambda: board_ui.show_temporary_message("获取用户详情失败", error_msg))
            else:
                print("公告板窗口不存在")
    # 处理其他类型的消息
    else:
        print(f"未知消息类型: {action}")

def send_message_to_server(message):
    try:
        msg = json.dumps(message).encode()
        msg_length = len(msg).to_bytes(4, byteorder='big')
        client_socket.sendall(msg_length + msg)
    except Exception as e:
        print(f"发送消息错误: {e}")
        messagebox.showerror("发送错误", f"发送消息失败: {e}")

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
        
        if not connected:
            self.show_temporary_message("连接错误", "无法连接到服务器")
            return
        
        # 发送登录请求到服务器
        login_request = {
            "action": "login",
            "username": username_or_email,
            "password": password
        }
        send_message_to_server(login_request)
        
    def login_success(self):
        self.show_temporary_message("登录成功", "登录成功")
        global current_user_is_login, board_ui
        current_user_is_login = True       
        self.master.withdraw()
        board_window = ttk.Window()
        style = ttk.Style()
        style.theme_use('')
        board_ui = BoardGUI(board_window, style)
    
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
        register_request = {
            "action": "register",
            "username": username,
            "password": password,
            "email": email,
            "college": college,
            "bio": bio
        }
        send_message_to_server(register_request)
    
    def register_success(self):
        self.show_temporary_message("注册成功", "注册成功，请登录")
        self.register_window.destroy()
        

class Announcement:
    def __init__(self, master, announcement_id, title, department, deadline, participants, initiator, announcement_type):
        self.frame = tk.Frame(master, bd=2, relief=tk.RIDGE, padx=10, pady=10)
        
        # 标题
        self.title_label = tk.Label(self.frame, text=title, font=('微软雅黑', 14, 'bold'), anchor='w')
        self.title_label.grid(row=0, column=0, columnspan=2, sticky='w', pady=5)
        
        # 院系
        self.department_label = tk.Label(self.frame, text=department, font=('微软雅黑', 12), anchor='w')
        self.department_label.grid(row=1, column=1, sticky='w', pady=2)
        
        # 截止时间
        deadline_formatted = deadline
        self.deadline_label = tk.Label(self.frame, text=f"截止时间：{deadline_formatted}", font=('微软雅黑', 12), anchor='w', fg='black')
        self.deadline_label.grid(row=3, column=0, sticky='w', pady=2)
        
        # 参与人数
        self.participants_label = tk.Label(self.frame, text=f"参与人数: {participants}", font=('微软雅黑', 12), anchor='w')
        self.participants_label.grid(row=2, column=1, sticky='w', pady=2)
        
        # 发起人
        self.initiator_label = tk.Label(self.frame, text=f"by {initiator}", font=('微软雅黑', 12), anchor='w')
        self.initiator_label.grid(row=1, column=0, sticky='w', pady=2)
        
        # 公告类型
        self.announcement_type_label = tk.Label(self.frame, text=announcement_type, font=('微软雅黑', 12), anchor='w')
        self.announcement_type_label.grid(row=2, column=0, sticky='w', pady=2)
        
        # 详情按钮
        self.details_button = tk.Button(self.frame, text="查看详情", command=lambda: self.show_details(announcement_id=announcement_id))
        self.details_button.grid(row=3, column=1, pady=2, sticky='e')
        
        self.frame.grid(sticky='nsew')
        self.announcement_id = announcement_id
    
    def show_details(self, announcement_id):
        # 从数据库中获取公告的具体内容
        self.show_temporary_message("获取详情", "正在获取公告详情...")
        send_message_to_server({
            "action": "show_announcement_detail",
            "announcement_id": announcement_id,
            "user_id": current_user_id
        })
            
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
    
class BoardGUI:
    def __init__(self, master, style=None):
        self.master = master
        self.master.title("公告板")
        self.master.geometry("800x600")
        self.master.resizable(width=True, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.detail_window = None
        self.publish_window = None
        
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
        
        self.announcements = []
        self.chatroom = None  # 添加一个属性用于存储当前聊天室
        # 初始显示所有公告
        self.show_all_announcements()
        
    def create_announcements(self, announcements_data):
        def update_grid(event=None):
            width = self.master.winfo_width()
            columns = max(1, width // 400)  # 每列宽度约为400像素
            for i, announcement in enumerate(self.announcements):
                announcement.frame.grid(row=i // columns, column=i % columns, padx=10, pady=10, sticky='nsew')

        for announcement_id, announcement_data in announcements_data.items():
            announcement = Announcement(self.scrollable_frame, announcement_id, announcement_data['headline'], announcement_data['college'], announcement_data['deadline'], announcement_data['join_num'], announcement_data['proposer_name'], announcement_data['type'])
            self.announcements.append(announcement)
            announcement_list[announcement_id] = announcement

        self.master.bind('<Configure>', update_grid)
        update_grid()
    
    def refresh(self, announcements_data=None):
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        announcement_list.clear()
        
        # 创建新的公告对象列表
        self.create_announcements(announcements_data)
        
    def show_detail_content(self, announcement_id, title, content, is_add_in):
        if self.detail_window and self.detail_window.winfo_exists():
            self.detail_window.destroy()
        self.detail_window = tk.Toplevel(self.master)
        self.detail_window.title("公告详情")
        self.detail_window.geometry("400x600")
        
        # 标题标签
        title_label = tk.Label(self.detail_window, text=title, font=('微软雅黑', 14, 'bold'), anchor='w')
        title_label.pack(pady=10)
        
        # 内容标签
        content_label = tk.Label(self.detail_window, text=content, font=('微软雅黑', 12), wraplength=380, justify='left')
        content_label.pack(pady=10)
        
        # 关注/取消关注按钮
        if is_add_in:
            disfollow_button = tk.Button(self.detail_window, text="取消关注", command=lambda: self.disfollow_announcement(current_user_id, announcement_id, self.detail_window))
            disfollow_button.pack(pady=10)
            # 进入聊天室按钮
            enter_chatroom_button = tk.Button(self.detail_window, text="进入聊天室", command=lambda: self.enter_chatroom(announcement_id))
            enter_chatroom_button.pack(pady=10)
        else:
            follow_button = tk.Button(self.detail_window, text="关注", command=lambda: self.follow_announcement(current_user_id, announcement_id, self.detail_window))
            follow_button.pack(pady=10)

    def enter_chatroom(self, announcement_id):
        chatroom_gui = ChatroomGUI(chat_id=announcement_id)
        chatroom_gui.run()
        active_chatrooms[announcement_id] = chatroom_gui
        
    def follow_announcement(self, user_id, announcement_id, show_details_window):
        request = {
            "action": "follow_announcement",
            "user_id": user_id,
            "announcement_id": announcement_id
        }
        send_message_to_server(request)
        self.detail_window.destroy()
            
    def disfollow_announcement(self, user_id, announcement_id, show_details_window):
        request = {
            "action": "disfollow_announcement",
            "user_id": user_id,
            "announcement_id": announcement_id
        }
        send_message_to_server(request)
        self.detail_window.destroy()
    
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
        if not current_user_is_login:
            self.show_temporary_message("发布失败", "请先登录")
            return
        
        if not current_user_id:
            self.show_temporary_message("发布失败", "用户ID无效")
            return
        
        if not cuurent_user_is_admin:
            self.show_temporary_message("发布失败", "只有管理员可以发布公告")
            return
        
        publish_window = ttk.Toplevel()
        publish_window.title("发布公告")
        publish_window.geometry("400x800")
        self.publish_window = publish_window
        
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
        
        # 截止时间标签和选择器
        deadline_label = tk.Label(publish_window, text="截止时间*:")
        deadline_label.pack(pady=10)
        
        # 使用ttkbootstrap的日期时间选择器
        deadline_entry = ttk.DateEntry(publish_window, bootstyle="primary", dateformat="%Y-%m-%d %H:%M:%S")
        deadline_entry.pack(pady=5)
        
        # 公告类型标签和选择器
        type_label = tk.Label(publish_window, text="公告类型*:")
        type_label.pack(pady=10)
        type_options = ["学业", "学术", "活动", "通知", "讲座", "比赛", "招聘", "志愿者", "社团活动", "研讨会", "其他"]
        type_entry = ttk.Combobox(publish_window, values=type_options, state='readonly')
        type_entry.pack(pady=5)
        type_entry.current(0)  # 默认选择第一个类型
        
        # 内容标签和输入框
        content_label = tk.Label(publish_window, text="内容*:")
        content_label.pack(pady=10)
        content_text = tk.Text(publish_window, height=10)
        content_text.pack(pady=5)
        
        # 提交按钮
        submit_button = tk.Button(publish_window, text="提交", command=lambda: self.submit_announcement(title_entry.get(), college_entry.get(), deadline_entry.entry.get(), type_entry.get(), content_text.get("1.0", tk.END), publish_window))
        submit_button.pack(pady=10)
        
    def submit_announcement(self, title, college, deadline, announcement_type, content, publish_window):
        if not title or not college or not deadline or not announcement_type or not content.strip():
            self.show_temporary_message("发布失败", "所有字段均为必填项")
            return
        request = {
            "action": "submit_announcement",
            "user_id": current_user_id,
            "username": current_username,
            "title": title,
            "college": college,
            "deadline": deadline,
            "type": announcement_type,
            "content": content
        }
        send_message_to_server(request)
    
    def on_closing(self):  
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.master.destroy()
            exit(0)
        else:
            pass
    
    def show_all_announcements(self):
        self.current_tab = "all"
        self.highlight_current_tab()
        # 向服务器请求所有公告数据
        request = {
            "action": "refresh_announcement",
            "user_id": current_user_id
        }
        send_message_to_server(request)
    
    def show_my_announcements(self):
        self.current_tab = "my"
        self.highlight_current_tab()
        # 清空当前公告
        for announcement in self.announcements:
            announcement.frame.destroy()
        self.announcements.clear()
        
        # 从服务器获取我加入的公告数据
        request = {
            "action": "refresh_my_announcement",
            "user_id": current_user_id
        }
        send_message_to_server(request)
    
    def highlight_current_tab(self):
        if self.current_tab == "all":
            self.all_announcements_button.config(relief="sunken", bg="lightblue")
            self.my_announcements_button.config(relief="raised", bg="SystemButtonFace")
        else:
            self.all_announcements_button.config(relief="raised", bg="SystemButtonFace")
            self.my_announcements_button.config(relief="sunken", bg="lightblue")
    
    
class ChatroomGUI:
    def __init__(self, chat_id):
        self.master = tk.Tk()
        self.chat_id = chat_id
        self.master.title("聊天室")
        self.master.geometry("800x600")
        self.master.resizable(width=False, height=True)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        active_chatrooms[chat_id] = self
        
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
        self.message_entry = tk.Text(self.master, font=('微软雅黑', 12), height=3, wrap='word')
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
        
    def on_close(self):
        self.master.destroy()
        del active_chatrooms[self.chat_id]
    
    def adjust_textbox_height(self, event=None):
        lines = int(self.message_entry.index('end-1c').split('.')[0])
        self.message_entry.config(height=max(3, lines))
        
    def on_mouse_wheel(self, event):
        SCROLL_THRESHOLD = 5  # 设置滚轮滚动距离阈值
        if event.delta > 0 and self.canvas.yview()[0] == 0.0:
            if abs(event.delta) >= SCROLL_THRESHOLD:
                self.refresh_older_messages()
        else:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
    def display_message(self, message, sender_id, sender_name="我", timestamp=None, to_bottom=True):
        # 创建一个消息框架
        message_frame = tk.Frame(self.scrollable_frame, bd=2, relief=tk.SUNKEN, padx=5, pady=5, width=780)
        
        # 创建一个内部框架用于纵向排列发送者和时间
        info_frame = tk.Frame(message_frame)
        info_frame.pack(side='left', fill='y', padx=5)
        
        # 显示发送者
        sender_label = tk.Label(info_frame, text=sender_name, font=('微软雅黑', 10, 'bold'), anchor='w', fg='blue', cursor="hand2")
        sender_label.pack(fill='x')
        sender_label.bind("<Button-1>", lambda e: self.request_user_details(sender_id, sender_name))
        
        # 显示发送时间
        if timestamp:
            # 假设 timestamp 是字符串
            time_diff = time.time() - time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
            if time_diff < 60:
                time_str = "刚刚"
            elif time_diff < 3600:
                time_str = f"{int(time_diff // 60)}分钟前"
            elif time_diff < 86400:
                time_str = f"{int(time_diff // 3600)}小时前"
            else:
                time_str = timestamp
        else:
            time_str = ""
        time_label = tk.Label(info_frame, text=time_str, font=('微软雅黑', 8), anchor='w')
        time_label.pack(fill='x')
        
        # 显示消息内容
        message_label = tk.Label(message_frame, text=message, font=('微软雅黑', 12), wraplength=700, justify='left')
        message_label.pack(side='left', fill='x', expand=True)
        
        if sender_id == current_user_id:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='e')
            message_frame.config(width=780)
            message_frame.config(highlightbackground='blue', highlightthickness=2)
            info_frame.pack(side='right', fill='y', padx=5)
            message_label.config(justify='right')
            message_label.pack_configure(side='right')
        else:
            message_frame.pack(fill='x', pady=5, padx=10, anchor='w')
            message_frame.config(width=780)
            message_frame.config(highlightbackground='gray', highlightthickness=1)
            info_frame.pack(side='left', fill='y', padx=5)
            message_label.config(justify='left')
            message_label.pack_configure(side='left')
        
        # 滚动到最新消息
        if to_bottom:
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(1.0)
        self.message_shown.append({
            "content": message,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "timestamp": timestamp
        })
        
    def display_messages_upper(self, json_messages):
        existed_messages = self.message_shown.copy()
        self.message_shown.clear()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for message in json_messages:
            self.display_message(message['content'], message['sender_id'], message['sender_name'], message['timestamp'], to_bottom=False)
            message_timestamp = time.mktime(time.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S'))
            if message_timestamp < self.oldest_timestamp:
                self.oldest_timestamp = message_timestamp
        for message in existed_messages:
            self.display_message(message['content'], message['sender_id'], message['sender_name'], message['timestamp'], to_bottom=False)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(0.0)
        
    def request_user_details(self, user_id, username):
        # 请求用户详情
        request = {
            "action": "show_user_details",
            "sender_id": user_id,
            "chat_id": self.chat_id
        }
        send_message_to_server(request)
        
    def show_user_details(self, user_id, username, email, college, is_admin, bio):
        # 显示用户详情的逻辑
            user_details_window = tk.Toplevel(self.master)
            user_details_window.title("用户详情")
            user_details_window.geometry("400x300")
            
            # 创建一个框架用于放置用户信息
            details_frame = tk.Frame(user_details_window, bd=2, relief=tk.RIDGE, padx=10, pady=10)
            details_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # 用户名和管理员标签
            username_frame = tk.Frame(details_frame)
            username_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
            username_title = tk.Label(username_frame, text=f"{username}", font=('微软雅黑', 14, 'bold'), fg='black')
            username_title.pack(side='left')
            if is_admin:
                admin_label = tk.Label(username_frame, text="管理员", font=('微软雅黑', 10), fg='red', bg='lightblue')
                admin_label.pack(side='left', padx=5)
            
            # 院系
            college_label = tk.Label(details_frame, text=f"{college}", font=('微软雅黑', 12), anchor='w')
            college_label.grid(row=1, column=0, sticky='w', pady=5)
            
            # 邮箱
            email_label = tk.Label(details_frame, text=f"{email}", font=('微软雅黑', 12), anchor='w')
            email_label.grid(row=1, column=1, sticky='w', pady=5)
            
            # 简介
            bio_label = tk.Label(details_frame, text=f"简介: {bio}", font=('微软雅黑', 12), wraplength=350, justify='left')
            bio_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=10)
        
    def send_message(self):
        # 发送消息的逻辑
        content = self.message_entry.get("1.0", tk.END).strip()
        if content and connected and current_user_id:
            message = {
                "action": "send_message",
                "sender_id": current_user_id,
                "chat_id": self.chat_id,
                "content": content
            }
            send_message_to_server(message)
            # self.display_message(message=content, sender_id=current_user_id, sender_name=current_username, timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))
            self.message_entry.delete("1.0", tk.END)
        elif not connected:
            self.show_temporary_message("发送失败", "未连接到服务器")
    
    def send_message_on_enter(self, event):
        # 调用发送消息方法，忽略事件对象
        self.send_message()
    
    def run(self):
        self.load_recent_messages()
        self.master.mainloop()
    
    def load_recent_messages(self):
        if not connected:
            self.show_temporary_message("连接错误", "未连接到服务器")
            return
    
        # 向服务器请求最近的消息
        request = {
            "action": "load_recent_messages",
            "chat_id": self.chat_id,
            "user_id": current_user_id,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')  # 当前时间作为参考
        }
        send_message_to_server(request)
    
    def refresh_older_messages(self):
        # 从服务器加载更早的消息
        if not connected:
            self.show_temporary_message("连接错误", "未连接到服务器")
            return
    
        # 向服务器请求更早的消息
        request = {
            "action": "refresh_older_messages",
            "chat_id": self.chat_id,
            "user_id": current_user_id,
            "oldest_timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.oldest_timestamp))  # 当前最旧的消息时间戳
        }
        send_message_to_server(request)


# 主程序
if __name__ == "__main__":
    # try:
    #     # 连接到数据库
    #     db = mysql.connector.connect(
    #         host="localhost",
    #         user="Haerxile",
    #         password="200518",
    #         database="COMM",
    #         consume_results=True 
    #     )
    #     cursor = db.cursor()
    #     print("数据库连接成功！")
    # except mysql.connector.Error as err:
    #     print(f"Error: {err}")
    #     messagebox.showerror("数据库连接错误", f"无法连接到数据库: {err}")
    #     exit(1)
    
    # 初始化数据库数据（保持不变）
    # ...

    # 在程序结束时删除测试数据
    # 保持不变
    
    # 创建主窗口，显示登录界面
    root = ttk.Window()
    style = ttk.Style()
    style.theme_use('')
    
    if root:
        # 连接到服务器
        connect_to_server()
    
    login_ui = LoginGUI(root)
    root.mainloop()
    
    # 关闭数据库连接
    # cursor.close()
    # db.close()