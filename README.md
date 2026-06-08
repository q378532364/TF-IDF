# 古典名著 RAG 问答系统

不基于向量数据库，基于sk-learn 词频算法，完成简易的RAG问答系统。
基于检索增强生成（RAG）的中国古典名著智能问答系统，支持**红楼梦**、**水浒传**、**西游记**三部名著。系统使用 TF-IDF 向量化 + 余弦相似度从原著中检索相关章节，结合 DeepSeek LLM 生成上下文相关的答案。

## 功能

- **多书支持** — 自动识别用户问题涉及哪部名著（关键词匹配 + LLM 回退）
- **RAG 检索** — TF-IDF 向量化 + 余弦相似度，检索 Top-5 相关章节
- **LLM 问答** — 基于检索到的原文内容生成答案，附来源引用
- **对话历史** — 保持多轮对话上下文
- **缓存机制** — 预处理数据自动缓存，加速启动

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API key
cp .env.example .env
# 编辑 .env，填入你的 API key

# 3. 运行
python rag.sys.py
```

## 配置

编辑 `.env` 文件：

| 变量              | 说明     | 默认值                        |
| ----------------- | -------- | ----------------------------- |
| `OPENAI_API_KEY`  | API 密钥 | —                             |
| `OPENAI_BASE_URL` | API 端点 | `https://api.deepseek.com/v1` |
| `AI_MODEL`        | 模型名称 | `deepseek-chat`               |

## 项目结构

```
python/
├── rag.sys.py              # 主程序（RAG 问答系统）
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── .env.example            # 配置模板
├── .gitignore              # Git 忽略规则
├── README.md               # 本文档
│
├── txt/                    # 原著数据
│   ├── 红楼梦/             # 80 个 .md 文件
│   ├── 水浒传/             # 目录 + 120 个 .html 文件
│   └── 西游记/             # 目录 + 100 个 .html 文件
│
├── cache/                  # 预处理缓存（自动生成）
│   ├── 红楼梦_chunks.pkl
│   ├── 红楼梦_vectors.pkl
│   ├── 水浒传_chunks.pkl
│   ├── 水浒传_vectors.pkl
│   ├── 西游记_chunks.pkl
│   └── 西游记_vectors.pkl
│
└── .history/               # 文件历史备份
```

## 架构

```
用户输入 → 书籍识别 → 向量检索 → LLM 问答 → 输出结果
              │            │           │
         关键词匹配    TF-IDF+余弦    DeepSeek API
         +LLM回退       相似度
```

### 核心流程

1. **书籍识别** — 通过角色/地名关键词匹配问题属于哪部书，不明确时调用 LLM 判断
2. **文档检索** — 对用户问题分词后 TF-IDF 向量化，与全书章节做余弦相似度，返回 Top-5
3. **答案生成** — 将检索到的章节内容作为上下文，调用 LLM 生成回答并引用来源

### 核心类

| 类            | 说明                                                |
| ------------- | --------------------------------------------------- |
| `SimpleTFIDF` | 纯 Python TF-IDF 向量化实现，支持 pickle 序列化缓存 |
| `RAGService`  | 主服务类，管理数据加载、检索、问答、对话历史        |

## 依赖

| 包              | 用途         |
| --------------- | ------------ |
| `requests`      | LLM API 调用 |
| `jieba`         | 中文分词     |
| `python-dotenv` | 环境变量加载 |

## 数据格式

### 红楼梦（Markdown）

```
### 【第X回】 标题
----
正文内容...
```

### 水浒传 / 西游记（HTML）

```html
<h1>第X回　标题</h1>
<p>正文内容...</p>
```
