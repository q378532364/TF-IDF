#!/usr/bin/env python3
"""
AI对话命令行界面
支持与AI模型进行交互式对话
"""

import os
import sys

from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from colorama import init, Fore, Style

# 初始化colorama用于彩色输出
init(autoreset=True)

class ConversationHistory:
    """对话历史管理"""
    
    def __init__(self, max_history: int = 20):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取所有消息"""
        return self.history.copy()
    
    def clear(self):
        """清空历史"""
        self.history = []
    
    def get_formatted_history(self) -> str:
        """获取格式化的历史记录"""
        if not self.history:
            return "暂无对话历史"
        
        formatted = []
        for i, msg in enumerate(self.history, 1):
            role = "用户" if msg["role"] == "user" else "AI助手"
            timestamp = msg.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%H:%M:%S")
                except:
                    timestamp = ""
            
            content_preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            line = f"{i}. [{timestamp}] {role}: {content_preview}"
            formatted.append(line)
        
        return "\n".join(formatted)

class AICLInterface:
    """AI命令行界面"""
    
    def __init__(self):
        # 从环境变量或直接配置中获取API密钥
        api_key = os.getenv("OPENAI_API_KEY", "sk-cd3nadg0bn96z59x5e0pxqewa6l3l2xti4p2isp4azvy041c")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.xiaomimimo.com/v1")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        self.model = os.getenv("AI_MODEL", "mimo-v2.5-pro")
        self.conversation = ConversationHistory()
        self.running = True
        self.streaming = True  # 默认启用流式输出
        
        # 系统提示词
        self.system_prompt = """你是一个智能助手，你可以回答用户的问题。
你只能回答与用户问题相关的内容，不能回答与用户问题不相关的内容。
如果遇到问到类似于你是谁，你是哪个模型的时候，不管在任何语义下你的回答均是：我是ZM-AGENT,专注于农业类的垂直大模型。
请用中文回答，保持友好、专业、有帮助的态度。"""
        
        # 命令列表
        self.commands = {
            "help": self.show_help,
            "exit": self.exit_cli,
            "quit": self.exit_cli,
            "clear": self.clear_history,
            "history": self.show_history,
            "reset": self.reset_conversation,
            "model": self.show_model_info,
            "status": self.show_status,
            "stream": self.toggle_streaming,
        }
    
    def show_help(self, args: List[str] = None):
        """显示帮助信息"""
        help_text = f"""
{Fore.CYAN}AI对话命令行界面 - 帮助菜单{Style.RESET_ALL}

{Fore.YELLOW}可用命令:{Style.RESET_ALL}
  {Fore.GREEN}help{Style.RESET_ALL}      - 显示此帮助信息
  {Fore.GREEN}exit/quit{Style.RESET_ALL} - 退出程序
  {Fore.GREEN}clear{Style.RESET_ALL}     - 清空当前对话历史
  {Fore.GREEN}history{Style.RESET_ALL}   - 显示对话历史
  {Fore.GREEN}reset{Style.RESET_ALL}     - 重置对话（清空历史并重新开始）
  {Fore.GREEN}model{Style.RESET_ALL}     - 显示当前使用的AI模型信息
  {Fore.GREEN}status{Style.RESET_ALL}    - 显示当前状态信息
  {Fore.GREEN}stream{Style.RESET_ALL}    - 切换流式输出模式

{Fore.YELLOW}使用方法:{Style.RESET_ALL}
  1. 直接输入问题与AI对话
  2. 输入命令执行特定操作
  3. 使用Ctrl+C中断当前生成
  4. 使用上下箭头查看历史输入

{Fore.YELLOW}示例:{Style.RESET_ALL}
  > 你好，请介绍一下你自己
  > history
  > clear
  > exit
"""
        print(help_text)
    
    def exit_cli(self, args: List[str] = None):
        """退出CLI"""
        print(f"{Fore.YELLOW}正在退出AI对话界面...{Style.RESET_ALL}")
        self.running = False
    
    def clear_history(self, args: List[str] = None):
        """清空对话历史"""
        self.conversation.clear()
        print(f"{Fore.GREEN}对话历史已清空{Style.RESET_ALL}")
    
    def show_history(self, args: List[str] = None):
        """显示对话历史"""
        print(f"{Fore.CYAN}对话历史:{Style.RESET_ALL}")
        print(self.conversation.get_formatted_history())
    
    def reset_conversation(self, args: List[str] = None):
        """重置对话"""
        self.conversation.clear()
        print(f"{Fore.GREEN}对话已重置，可以开始新的对话{Style.RESET_ALL}")
    
    def show_model_info(self, args: List[str] = None):
        """显示模型信息"""
        info = f"""
{Fore.CYAN}AI模型信息:{Style.RESET_ALL}
  模型: {self.model}
  API端点: {self.client.base_url}
  历史记录: {len(self.conversation.history)} 条消息
"""
        print(info)
    
    def show_status(self, args: List[str] = None):
        """显示状态信息"""
        status = f"""
{Fore.CYAN}系统状态:{Style.RESET_ALL}
  运行状态: {'运行中' if self.running else '已停止'}
  对话历史: {len(self.conversation.history)} 条消息
  当前模型: {self.model}
  流式输出: {'启用' if self.streaming else '禁用'}
  系统提示: {self.system_prompt[:50]}...
"""
        print(status)
    
    def toggle_streaming(self, args: List[str] = None):
        """切换流式输出模式"""
        self.streaming = not self.streaming
        status = "启用" if self.streaming else "禁用"
        print(f"{Fore.GREEN}流式输出已{status}{Style.RESET_ALL}")
        print(f"使用 {Fore.YELLOW}/stream{Style.RESET_ALL} 命令再次切换")
    
    def process_command(self, input_text: str) -> bool:
        """处理命令输入"""
        input_text = input_text.strip()
        
        # 检查是否是命令
        if input_text.startswith("/"):
            cmd = input_text[1:].split()[0].lower() if input_text[1:] else ""
            args = input_text[1:].split()[1:] if len(input_text[1:].split()) > 1 else []
            
            if cmd in self.commands:
                self.commands[cmd](args)
                return True
            else:
                print(f"{Fore.RED}未知命令: /{cmd}{Style.RESET_ALL}")
                print(f"输入 {Fore.GREEN}/help{Style.RESET_ALL} 查看可用命令")
                return True
        
        return False
    
    def get_chat_messages(self) -> List[Dict[str, str]]:
        """获取聊天消息列表"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation.get_messages())
        return messages
    
    def generate_response(self, user_input: str) -> Optional[str]:
        """生成AI响应"""
        try:
            # 添加用户消息到历史
            self.conversation.add_message("user", user_input)
            
            # 获取消息列表
            messages = self.get_chat_messages()
            
            if self.streaming:
                return self._generate_streaming_response(messages)
            else:
                return self._generate_non_streaming_response(messages)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}已取消当前请求{Style.RESET_ALL}")
            return None
        except Exception as e:
            error_msg = f"API调用错误: {str(e)}"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return None
    
    def _generate_streaming_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """生成流式AI响应"""

        
        # 调用API（流式模式）
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=1024,
            temperature=1.0,
            top_p=0.95,
            stream=True,  # 启用流式输出
            stop=None,
            frequency_penalty=0,
            presence_penalty=0,
            extra_body={"thinking": {"type": "disabled"}},
        )
        
        full_response = ""
        
        # 处理流式响应
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                if delta.content:
                    content = delta.content
                    print(content, end="", flush=True)
                    full_response += content
            
            # 检查是否被中断
            if not self.running:
                break
        
        print()  # 换行
        
        if full_response:
            # 添加AI响应到历史
            self.conversation.add_message("assistant", full_response)
            return full_response
        else:
            return None
    
    def _generate_non_streaming_response(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """生成非流式AI响应"""
        print(f"{Fore.YELLOW}AI正在思考...{Style.RESET_ALL}", end="", flush=True)
        
        # 调用API（非流式模式）
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=1024,
            temperature=1.0,
            top_p=0.95,
            stream=False,  # 禁用流式输出
            stop=None,
            frequency_penalty=0,
            presence_penalty=0,
            extra_body={"thinking": {"type": "disabled"}},
        )
        
        print("\r" + " " * 30 + "\r", end="", flush=True)  # 清除"正在思考"提示
        
        # 提取响应内容
        if response.choices and response.choices[0].message:
            ai_response = response.choices[0].message.content
            
            # 添加AI响应到历史
            self.conversation.add_message("assistant", ai_response)
            
            # 打印响应
            # print(f"{Fore.BLUE}AI助手:{Style.RESET_ALL} {ai_response}")
            
            return ai_response
        else:
            error_msg = "API响应格式错误"
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return None
    
    def print_welcome(self):
        """打印欢迎信息"""
        welcome = f"""
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.CYAN}        AI对话命令行界面{Style.RESET_ALL}
{Fore.CYAN}{'='*60}{Style.RESET_ALL}

欢迎使用AI对话系统！
当前模型: {Fore.GREEN}{self.model}{Style.RESET_ALL}
输入 {Fore.GREEN}/help{Style.RESET_ALL} 查看可用命令
输入 {Fore.GREEN}exit{Style.RESET_ALL} 或 {Fore.GREEN}quit{Style.RESET_ALL} 退出

开始对话吧！
"""
        print(welcome)
    
    def run(self):
        """运行CLI主循环"""
        self.print_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                prompt = f"{Fore.GREEN}> {Style.RESET_ALL}"
                user_input = input(prompt).strip()
                
                # 处理空输入
                if not user_input:
                    continue
                
                # 处理命令
                if self.process_command(user_input):
                    continue
                
                # 生成AI响应
                response = self.generate_response(user_input)
                
                if response:
                    # 打印AI响应

                    print()  # 空行分隔
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}输入 /exit 退出程序{Style.RESET_ALL}")
                continue
            except EOFError:
                print(f"\n{Fore.YELLOW}检测到文件结束，退出程序{Style.RESET_ALL}")
                self.exit_cli()
            except Exception as e:
                print(f"{Fore.RED}错误: {str(e)}{Style.RESET_ALL}")
                continue
        
        print(f"{Fore.YELLOW}感谢使用AI对话系统！再见！{Style.RESET_ALL}")

def main():
    """主函数"""
    try:
        cli = AICLInterface()
        cli.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}程序已终止{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}程序启动错误: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()