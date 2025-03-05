# TXT 转 TTS 语音工具

基于 chatTTS-ui API 的批量文本转语音桌面应用，支持自动下载生成的语音文件。

## 功能特性
- 📁 图形化界面操作
- 📄 支持批量处理 txt 文件（按行转换）
- 🔊 自动下载生成的语音文件
- ⚙️ 可配置音色参数和生成参数
- 🚀 多线程处理避免界面卡顿

## 快速开始

### 前置要求
1. 已安装 Python 3.8+
2. 本地运行 [chatTTS-ui](https://github.com/jianfcpku/chatTTS-ui) 服务
3. 安装依赖库：
    ```bash
    pip install requests tkinter


    默认配置（可在 tts_synthesis() 函数中修改）：
    {
        "voice": "seed_357_restored_emb-covert",
        "prompt": "[break_6]",
        "temperature": 0.3,
        "top_p": 0.7,
        "top_k": 20
    }


### 注意事项
- 确保 chatTTS-ui 服务运行在 http://127.0.0.1:9966
- 生成文件保存至 TTS_downloads 目录
- 文件名自动清理特殊字符并截断至50字符
- 网络异常时会自动跳过失败项
