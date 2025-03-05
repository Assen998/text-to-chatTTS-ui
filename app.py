import requests
import threading
import re
import os
import tkinter as tk
from tkinter import ttk, filedialog

def tts_synthesis(text: str):
    try:
        res = requests.post('http://127.0.0.1:9966/tts', data={
            "text": text,
            "voice": "seed_357_restored_emb-covert",          # 默认音色值
            "prompt": "[break_6]",             # 恢复默认空字符串
            "temperature": 0.3,
            "top_p": 0.7,
            "top_k": 20,
            "skip_refine": 0,
        })
        res.raise_for_status()
        
        response = res.json()
        if response.get('code') == 0:
            # 已正确返回url列表
            return [audio['url'] for audio in response['audio_files']]
        print(f"API错误: {response.get('msg')}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except ValueError:
        print("响应解析失败")
        return None

def split_text_file(file_path: str) -> list:
    """
    读取文本文件并按换行符切分为数组
    
    参数:
        file_path (str): 文本文件路径
        
    返回:
        list: 包含每行文本的数组，出错返回空列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取文件内容并去除空行
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"文件读取失败: {str(e)}")
        return []

def sanitize_filename(text: str) -> str:
    """清理非法文件名字符"""
    return re.sub(r'[\\/*?:"<>|]', '_', text)[:50]  # 保留前50个字符

def download_audio(url: str, filename: str, save_dir: str = "downloads"):
    """下载音频文件"""
    try:
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"{filename}.wav")
        
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return filepath
    except Exception as e:
        print(f"下载失败 {filename}: {str(e)}")
        return None

# 新增处理流程
def process_text_file(file_path: str):
    texts = split_text_file(file_path)
    for idx, text in enumerate(texts, 1):
        # 合成语音
        urls = tts_synthesis(text)
        if not urls:
            continue
            
        # 下载首个音频（通常只有一个）
        filename = f"{idx}_{sanitize_filename(text)}"  # 保持索引在前
        saved_path = download_audio(urls[0], filename)
        if saved_path:
            print(f"已保存: {saved_path}")

class TTSApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("TXT to TTS")  # 修改窗口标题
        self.window.geometry("400x400")  # 设置初始窗口尺寸
        self.setup_ui()
        
        # 初始化下载目录
        self.download_dir = os.path.join(os.getcwd(), "TTS_downloads")
        os.makedirs(self.download_dir, exist_ok=True)
    # 先定义select_file再定义setup_ui
    def select_file(self):
        """选择文件"""
        self.file_path = filedialog.askopenfilename(
            filetypes=[("文本文件", "*.txt")])
        if self.file_path:
            self.status.config(text=f"已选择文件: {os.path.basename(self.file_path)}", 
                             foreground="green")
            self.start_btn.config(state="normal")
    def start_processing(self):  # 先定义按钮回调方法
        """启动处理线程"""
        self.file_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.status.config(text="处理中...", foreground="blue")
        
        # 创建后台线程
        threading.Thread(target=self.process_file, daemon=True).start()

    def setup_ui(self):  # 最后定义界面布局方法
        """创建界面组件"""
        # 主框架布局到窗口中心
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        frame = ttk.Frame(self.window, padding=20)
        frame.grid(row=0, column=0, sticky="nsew")
        # 组件容器居中布局
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # 文件选择区域
        ttk.Label(frame, text="选择一个txt文件\r\n按行传给tts-ui的api\r\n自动下载语音文件到当前目录下的TTS_downloads",foreground="gray",anchor="center",wraplength=400,).grid(row=0, column=0, sticky="w")
        self.file_btn = ttk.Button(frame, text="浏览...", command=self.select_file)
        self.file_btn.grid(row=1, column=0)
        # 状态显示
        self.status = ttk.Label(frame, text="就绪", foreground="gray")
        self.status.grid(row=2, column=0, pady=10)
        # 操作按钮
        self.start_btn = ttk.Button(frame, text="开始转换", state="disabled", 
                                  command=self.start_processing)
        self.start_btn.grid(row=3, column=0)

        ttk.Label(frame, text="Powered by Assen998",foreground="blue",anchor="center",wraplength=400,).grid(row=5, column=0, sticky="w")
        # 添加底部空白区域使整体垂直居中
        frame.grid_rowconfigure(4, weight=1)

    def process_file(self):
        """实际处理逻辑"""
        texts = split_text_file(self.file_path)
        total = len(texts)
        
        # 获取不带扩展名的文件名创建二级目录
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
        txt_dir = os.path.join(self.download_dir, sanitize_filename(base_name))
        os.makedirs(txt_dir, exist_ok=True)
        
        for idx, text in enumerate(texts, 1):
            self.update_status(f"正在处理 {idx}/{total}: {text[:20]}...")
            urls = tts_synthesis(text)
            
            if urls:
                filename = f"{idx}_{sanitize_filename(text)}"
                download_audio(urls[0], filename, txt_dir)  # 修改此处传入二级目录
        
        self.window.after(0, lambda: self.status.config(
            text=f"完成！文件保存在: {txt_dir}",  # 更新完成提示路径
            foreground="green"))
        self.window.after(0, lambda: self.file_btn.config(state="normal"))

    def update_status(self, message):
        """线程安全的状态更新"""
        self.window.after(0, lambda: self.status.config(text=message))
    def run(self):
        self.window.mainloop()
# 启动程序
if __name__ == "__main__":
    TTSApp().run()
