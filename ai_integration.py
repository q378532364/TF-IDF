#!/usr/bin/env python3
"""
AI模型集成模块
支持多种在线AI模型API
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIModelConfig:
    """AI模型配置管理"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "enabled": bool(os.getenv("OPENAI_API_KEY"))
            },
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
                "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "enabled": bool(os.getenv("DEEPSEEK_API_KEY"))
            },
            "common": {
                "max_tokens": int(os.getenv("MAX_TOKENS", 2000)),
                "temperature": float(os.getenv("TEMPERATURE", 0.7)),
                "timeout": int(os.getenv("TIMEOUT", 30))
            }
        }
        return config
    
    def get_available_models(self) -> List[str]:
        """获取可用的AI模型"""
        available = []
        for model_name, model_config in self.config.items():
            if model_name != "common" and model_config.get("enabled", False):
                available.append(model_name)
        return available
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的配置"""
        if model_name in self.config and model_name != "common":
            return self.config[model_name]
        return None

class BaseAIModel:
    """AI模型基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = "base"
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成响应（子类必须实现）"""
        raise NotImplementedError
    
    def _format_response(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """格式化响应"""
        if metadata is None:
            metadata = {}
        
        return {
            "content": content,
            "model": self.name,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }

class OpenAIModel(BaseAIModel):
    """OpenAI模型集成"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "openai"
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI库未安装，请运行: pip install openai")
        
        self.client = OpenAI(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用OpenAI API生成响应"""
        try:
            model = kwargs.get("model", self.config.get("model", "gpt-3.5-turbo"))
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个有帮助的AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=kwargs.get("timeout", 30)
            )
            
            content = response.choices[0].message.content
            metadata = {
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
            return self._format_response(content, metadata)
            
        except Exception as e:
            return self._format_response(f"OpenAI API错误: {str(e)}", {"error": str(e)})

class DeepSeekModel(BaseAIModel):
    """DeepSeek模型集成"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "deepseek"
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用DeepSeek API生成响应"""
        try:
            api_key = self.config.get("api_key", "")
            base_url = self.config.get("base_url", "https://api.deepseek.com")
            model = kwargs.get("model", self.config.get("model", "deepseek-chat"))
            max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens", 2000))
            temperature = kwargs.get("temperature", self.config.get("temperature", 0.7))
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个有帮助的AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=kwargs.get("timeout", 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                metadata = {
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model),
                    "finish_reason": result["choices"][0].get("finish_reason", "stop")
                }
                
                return self._format_response(content, metadata)
            else:
                error_msg = f"DeepSeek API错误: {response.status_code} - {response.text}"
                return self._format_response(error_msg, {"error": error_msg})
                
        except Exception as e:
            return self._format_response(f"DeepSeek API错误: {str(e)}", {"error": str(e)})

class MockAIModel(BaseAIModel):
    """模拟AI模型（用于测试）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.name = "mock"
    
    def generate_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """生成模拟响应"""
        # 模拟AI思考时间
        time.sleep(0.5)
        
        # 基于提示生成模拟响应
        prompt_length = len(prompt)
        keyword_count = len(prompt.split())
        
        response_content = f"""基于您提供的文本（长度: {prompt_length}字符，约{keyword_count}个词），我进行了分析：

主要发现：
1. 文本包含多个关键概念
2. 主题涉及多个相关领域
3. 需要进一步深入分析具体细节

建议：
- 提供更具体的上下文信息
- 明确您希望分析的方向
- 考虑相关历史数据的对比

这是一个模拟响应。在实际使用中，这将由真实的AI模型生成。"""
        
        metadata = {
            "usage": {
                "prompt_tokens": prompt_length,
                "completion_tokens": 150,
                "total_tokens": prompt_length + 150
            },
            "model": "mock-model-v1",
            "finish_reason": "stop"
        }
        
        return self._format_response(response_content, metadata)

class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self):
        self.config_manager = AIModelConfig()
        self.models = self._initialize_models()
    
    def _initialize_models(self) -> Dict[str, BaseAIModel]:
        """初始化所有可用的AI模型"""
        models = {}
        
        # 检查并初始化OpenAI
        openai_config = self.config_manager.get_model_config("openai")
        if openai_config and openai_config.get("enabled", False):
            try:
                models["openai"] = OpenAIModel(openai_config)
            except Exception as e:
                print(f"初始化OpenAI模型失败: {e}")
        
        # 检查并初始化DeepSeek
        deepseek_config = self.config_manager.get_model_config("deepseek")
        if deepseek_config and deepseek_config.get("enabled", False):
            try:
                models["deepseek"] = DeepSeekModel(deepseek_config)
            except Exception as e:
                print(f"初始化DeepSeek模型失败: {e}")
        
        # 总是添加模拟模型作为后备
        models["mock"] = MockAIModel()
        
        return models
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self.models.keys())
    
    def get_model(self, model_name: str) -> Optional[BaseAIModel]:
        """获取指定的模型实例"""
        return self.models.get(model_name)
    
    def generate_response(self, model_name: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """使用指定模型生成响应"""
        model = self.get_model(model_name)
        if not model:
            available_models = self.get_available_models()
            return {
                "content": f"模型 '{model_name}' 不可用。可用模型: {', '.join(available_models)}",
                "model": "error",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": f"模型不可用: {model_name}"}
            }
        
        return model.generate_response(prompt, **kwargs)
    
    def batch_generate(self, prompts: List[str], model_name: str = "mock", **kwargs) -> List[Dict[str, Any]]:
        """批量生成响应"""
        results = []
        for i, prompt in enumerate(prompts, 1):
            print(f"处理提示 {i}/{len(prompts)}...")
            result = self.generate_response(model_name, prompt, **kwargs)
            results.append(result)
        
        return results

def test_ai_integration():
    """测试AI集成功能"""
    print("测试AI集成模块...")
    
    # 创建模型管理器
    manager = AIModelManager()
    
    # 显示可用模型
    available_models = manager.get_available_models()
    print(f"可用模型: {', '.join(available_models)}")
    
    # 测试每个模型
    test_prompt = "请简要介绍人工智能的发展历史。"
    
    for model_name in available_models:
        print(f"\n使用 {model_name} 模型测试...")
        print(f"提示: {test_prompt}")
        
        start_time = time.time()
        response = manager.generate_response(model_name, test_prompt)
        elapsed_time = time.time() - start_time
        
        print(f"响应时间: {elapsed_time:.2f}秒")
        print(f"模型: {response.get('model')}")
        print(f"响应内容: {response.get('content', '')[:200]}...")
        
        if "metadata" in response:
            usage = response["metadata"].get("usage", {})
            if usage:
                print(f"使用统计: {usage}")

if __name__ == "__main__":
    test_ai_integration()