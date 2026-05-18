# AI对话命令行界面

这是一个支持流式输出的AI对话命令行界面，基于OpenAI API。

## 功能特性

- ✅ **流式输出**：实时显示AI响应，字符逐个显示
- ✅ **对话历史**：自动保存对话历史，支持查看和清空
- ✅ **命令系统**：丰富的内置命令
- ✅ **彩色输出**：使用colorama提供更好的视觉体验
- ✅ **可配置**：支持环境变量配置API密钥和模型
- ✅ **错误处理**：完善的错误处理和中断支持

## 安装依赖

```bash
pip install openai colorama
```

或者使用项目中的requirements.txt：
```bash
pip install -r requirements.txt
```

## 使用方法

### 启动程序

```bash
python index.py
```

### 基本对话

启动后，直接输入问题即可与AI对话：

```
> 你好，请介绍一下你自己
AI助手: 你好！我是一个智能助手，我可以回答你的问题...
```

### 可用命令

所有命令以 `/` 开头：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/exit` 或 `/quit` | 退出程序 |
| `/clear` | 清空当前对话历史 |
| `/history` | 显示对话历史 |
| `/reset` | 重置对话（清空历史并重新开始） |
| `/model` | 显示当前使用的AI模型信息 |
| `/status` | 显示当前状态信息 |
| `/stream` | 切换流式输出模式 |

### 流式输出控制

默认启用流式输出，AI响应会实时显示。可以使用 `/stream` 命令切换：

- 启用流式输出：AI响应实时显示
- 禁用流式输出：显示"AI正在思考..."提示，完成后一次性显示响应

### 环境变量配置

可以通过环境变量配置API设置：

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here
set OPENAI_BASE_URL=https://api.xiaomimimo.com/v1
set AI_MODEL=mimo-v2.5-pro

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
export OPENAI_BASE_URL=https://api.xiaomimimo.com/v1
export AI_MODEL=mimo-v2.5-pro
```

如果不设置环境变量，程序会使用内置的默认配置。

## 快捷键

- **Ctrl+C**：中断当前AI响应生成
- **上下箭头**：查看历史输入
- **Ctrl+D** (Linux/Mac) 或 **Ctrl+Z** (Windows)：退出程序

## 代码结构

```
index.py
├── ConversationHistory  # 对话历史管理
│   ├── add_message()    # 添加消息
│   ├── get_messages()   # 获取消息列表
│   ├── clear()          # 清空历史
│   └── get_formatted_history()  # 格式化显示
│
└── AICLInterface        # 命令行界面
    ├── generate_response()      # 生成AI响应
    ├── _generate_streaming_response()   # 流式输出
    ├── _generate_non_streaming_response() # 非流式输出
    ├── toggle_streaming()       # 切换流式模式
    └── 其他命令方法...
```

## 示例会话

```
============================================================
        AI对话命令行界面
============================================================

欢迎使用AI对话系统！
当前模型: mimo-v2.5-pro
输入 /help 查看可用命令
输入 exit 或 quit 退出

开始对话吧！

> /status

系统状态:
  运行状态: 运行中
  对话历史: 0 条消息
  当前模型: mimo-v2.5-pro
  流式输出: 启用
  系统提示: 你是一个智能助手，你可以回答用户的问题...

> 请用中文写一首关于春天的诗
AI助手: 春风轻拂柳丝长，桃花含笑映朝阳。
        溪水潺潺歌不断，燕子归来筑巢忙。
        绿草如茵铺满地，百花争艳吐芬芳。
        春光明媚人心醉，万物复苏展新装。

> /history

对话历史:
1. [14:30:25] 用户: 请用中文写一首关于春天的诗
2. [14:30:28] AI助手: 春风轻拂柳丝长，桃花含笑映朝阳。溪水潺潺歌不断...

> /stream
流式输出已禁用

> 请介绍一下人工智能
AI正在思考...
AI助手: 人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支...

> /exit
正在退出AI对话界面...
感谢使用AI对话系统！再见！
```

## 注意事项

1. **API密钥安全**：建议使用环境变量配置API密钥，避免在代码中硬编码
2. **网络连接**：需要稳定的网络连接访问API服务
3. **流式输出**：在慢速网络环境下，流式输出可能会有延迟
4. **历史限制**：默认保存最近20条消息，可通过修改代码调整

## 故障排除

### 常见问题

1. **导入错误**：确保已安装所有依赖包
2. **API连接失败**：检查网络连接和API密钥
3. **编码问题**：在Windows上如果遇到编码错误，可以修改代码避免特殊字符

### 调试模式

如需调试，可以修改代码中的异常处理部分，打印更详细的错误信息。

## 扩展开发

### 添加新命令

在 `AICLInterface.__init__()` 的 `commands` 字典中添加新命令：

```python
self.commands = {
    # ... 现有命令
    "newcmd": self.new_command_method,
}
```

### 修改系统提示

修改 `system_prompt` 变量可以改变AI的行为和风格。

### 支持其他AI模型

可以扩展代码以支持其他AI API，参考现有的OpenAI集成模式。