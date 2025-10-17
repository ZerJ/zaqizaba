import tkinter as tk
from tkinter import messagebox


class ConcertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("演唱会购票系统")
        self.root.geometry("800x600")

        # 创建左侧展示区域
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_label = tk.Label(self.left_frame, text="信息展示区", font=("Arial", 14))
        self.show_label.pack(pady=20)
        self.info_text = tk.Text(self.left_frame, height=20, width=40)
        self.info_text.pack()

        # 创建右侧操作区域
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 账号登录部分
        self.login_frame = tk.Frame(self.right_frame)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="账号:").grid(row=0, column=0)
        self.account_entry = tk.Entry(self.login_frame)
        self.account_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="密码:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="登录", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        # 演唱会选择部分
        self.concert_frame = tk.Frame(self.right_frame)
        self.concert_frame.pack(pady=20)

        tk.Label(self.concert_frame, text="选择演唱会:").pack()
        self.concert_options = ["演唱会 A", "演唱会 B", "演唱会 C"]
        self.concert_var = tk.StringVar()
        self.concert_var.set(self.concert_options[0])
        self.concert_menu = tk.OptionMenu(self.concert_frame, self.concert_var, *self.concert_options)
        self.concert_menu.pack()

        self.select_button = tk.Button(self.concert_frame, text="选择", command=self.select_concert)
        self.select_button.pack(pady=10)

        self.is_logged_in = False

    def login(self):
        account = self.account_entry.get()
        password = self.password_entry.get()
        # 这里简单模拟登录，实际应与后端交互验证
        if account and password:
            self.is_logged_in = True
            messagebox.showinfo("登录成功", "登录成功！")
            self.info_text.insert(tk.END, f"用户 {account} 登录成功\n")
        else:
            messagebox.showerror("登录失败", "请输入账号和密码！")

    def select_concert(self):
        if not self.is_logged_in:
            messagebox.showerror("未登录", "请先登录！")
            return
        selected_concert = self.concert_var.get()
        self.info_text.insert(tk.END, f"您选择了 {selected_concert}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConcertApp(root)
    root.mainloop()