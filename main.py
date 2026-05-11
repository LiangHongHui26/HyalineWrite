import tkinter as tk
import os

class StealthEditor:
    def __init__(self, root):
        self.root = root
        # 取消系统自带的边框和标题栏
        self.root.overrideredirect(True)
        # 保持窗口在最前端
        self.root.attributes('-topmost', True) 

        # 定义一种极难与正常像素撞车的颜色作为“透明色扣像键”
        self.TRANS_COLOR = '#010203'
        self.root.wm_attributes('-transparentcolor', self.TRANS_COLOR)
        self.root.config(bg=self.TRANS_COLOR)

        self.save_file = "stealth_novel.txt"

        self.is_minimized = False
        self.normal_geometry = "600x400+200+200"
        
        self.setup_ui()
        self.load_file()
        self.auto_save()
        
        # 启动时默认进入普通模式
        self.switch_to_normal()

    def setup_ui(self):
        # 1. 浅蓝色标题栏
        self.title_bar = tk.Frame(self.root, bg='lightblue', height=28)
        self.title_bar.pack_propagate(False)

        # 标题文字
        self.title_label = tk.Label(self.title_bar, text="TxT", bg='lightblue', fg='#333333', font=('Microsoft YaHei', 9))
        self.title_label.pack(side='left', padx=10)

        # 绑定移动事件
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.do_move)

        # 右侧按钮：关闭
        self.close_btn = tk.Button(self.title_bar, text='×', bg='lightblue', activebackground='#ff5c5c', bd=0, width=3, command=self.close_app)
        self.close_btn.pack(side='right')

        # 右侧按钮：最小化 (卷起效果)
        self.min_btn = tk.Button(self.title_bar, text='—', bg='lightblue', activebackground='#99ccee', bd=0, width=3, command=self.toggle_minimize)
        self.min_btn.pack(side='right')

        # 右侧按钮：模式切换 (点击后进入极限隐蔽模式)
        self.mode_btn = tk.Button(self.title_bar, text='[隐藏]', bg='lightblue', bd=0, command=self.switch_to_stealth)
        self.mode_btn.pack(side='right', padx=10)

        # 2. 文本输入区域
        self.text_frame = tk.Frame(self.root, bg=self.TRANS_COLOR)
        self.text_frame.pack(fill='both', expand=True)

        self.text_area = tk.Text(
            self.text_frame,
            font=('Microsoft YaHei', 12),
            bd=0,
            highlightthickness=0,
            wrap='word',
            selectbackground='#0078D7',      
            selectforeground='white',
            padx=5, 
            pady=5,
            undo=True,            
            autoseparators=True,  
            maxundo=-1,            
             cursor='xterm'
        )
        self.text_area.pack(fill='both', expand=True)

        # 绑定撤销(Ctrl+Z)和重做(Ctrl+Y)快捷键
        self.text_area.bind('<Control-z>', self.undo_action)
        self.text_area.bind('<Control-y>', self.redo_action)

        # 3. 调整大小的拖拽抓手 (放置在右下角)
        self.grip = tk.Frame(self.root, bg='lightblue', width=12, height=12, cursor='bottom_right_corner')
        self.grip.bind('<Button-1>', self.start_resize)
        self.grip.bind('<B1-Motion>', self.do_resize)

        # 4. 极限隐形模式下的“恢复小图标”
        self.stealth_icon = tk.Label(
            self.root, 
            text='',           
            bg='#e0e0e0',      
            cursor='hand2'
        )
        
        # 为小圆点绑定不同的鼠标事件
        self.stealth_icon.bind('<Button-1>', self.regain_focus)         
        self.stealth_icon.bind('<Button-3>', self.switch_to_normal)     
        self.stealth_icon.bind('<Double-Button-1>', self.switch_to_normal) 

        # 初始化窗口尺寸
        self.root.geometry(self.normal_geometry)

    # =============== 撤销与重做逻辑 ===============
    def undo_action(self, event=None):
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            pass 
        return "break" 

    def redo_action(self, event=None):
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            pass 
        return "break"

    # =============== 核心逻辑 ===============
    def regain_focus(self, event=None):
        self.root.focus_force()
        self.text_area.focus_set()
        
        self.stealth_icon.config(bg='#ff8888')
        self.root.after(400, lambda: self.stealth_icon.config(bg='#d0d0d0'))

    def switch_to_stealth(self):
        if self.is_minimized:
            self.toggle_minimize()

        self.title_bar.pack_forget()
        self.grip.place_forget()

        self.stealth_icon.place(relx=1.0, x=-12, y=0, width=12, height=12)

        # 【修复点】：修改点阵字体并隐藏鼠标选中背景色
        self.text_area.config(
            bg=self.TRANS_COLOR, 
            fg=self.TRANS_COLOR, 
            insertbackground=self.TRANS_COLOR,
            selectbackground=self.TRANS_COLOR, # 隐藏拖动选中时的蓝色底色块
            selectforeground=self.TRANS_COLOR, # 隐藏选中时的字色
            font=('Terminal', 12)              # 切换无抗锯齿的点阵字体，根除残留杂边！
        )
        self.text_area.focus_set()

    def switch_to_normal(self, event=None):
        self.stealth_icon.place_forget()

        self.title_bar.pack(before=self.text_frame, fill='x', side='top')
        self.grip.place(relx=1.0, rely=1.0, anchor='se')

        # 【恢复点】：将参数恢复到正常的抗锯齿字体和普通颜色
        self.text_area.config(
            bg='#A9A9A9', 
            fg='#777E88', 
            insertbackground='white',
            insertwidth=2,
            selectbackground='#0078D7',        # 恢复正常的选中高亮
            selectforeground='white',
            font=('Microsoft YaHei', 12)       # 恢复微软雅黑抗锯齿字体
        )
        self.text_area.focus_set()

    # =============== 其他辅助功能 ===============
    def toggle_minimize(self):
        if not self.is_minimized:
            self.normal_geometry = self.root.geometry()
            self.text_frame.pack_forget()
            self.grip.place_forget()
            self.root.geometry(f"{self.root.winfo_width()}x28")
            self.is_minimized = True
        else:
            self.text_frame.pack(fill='both', expand=True)
            self.grip.place(relx=1.0, rely=1.0, anchor='se')
            self.root.geometry(self.normal_geometry)
            self.is_minimized = False

    def auto_save(self):
        try:
            content = self.text_area.get(1.0, tk.END)
            with open(self.save_file, 'w', encoding='utf-8') as f:
                f.write(content[:-1])
        except Exception:
            pass
        self.root.after(5000, self.auto_save)

    def load_file(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.text_area.insert(1.0, content)
                self.text_area.edit_reset()

    def close_app(self):
        content = self.text_area.get(1.0, tk.END)
        with open(self.save_file, 'w', encoding='utf-8') as f:
            f.write(content[:-1])
        self.root.destroy()

    def start_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self.start_x
        y = self.root.winfo_y() + event.y - self.start_y
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.resize_start_x = event.x_root
        self.resize_start_y = event.y_root
        self.resize_start_w = self.root.winfo_width()
        self.resize_start_h = self.root.winfo_height()

    def do_resize(self, event):
        new_w = self.resize_start_w + (event.x_root - self.resize_start_x)
        new_h = self.resize_start_h + (event.y_root - self.resize_start_y)
        if new_w > 150 and new_h > 50:
            self.root.geometry(f"{new_w}x{new_h}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StealthEditor(root)
    root.mainloop()