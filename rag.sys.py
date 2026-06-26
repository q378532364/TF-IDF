import os
import pickle
import sys
import re
import math
import json
import logging
import requests
import urllib.request
from collections import Counter
from dotenv import load_dotenv
from pathlib import Path
import jieba

# 设置 jieba 日志级别以抑制初始化消息
jieba.setLogLevel(logging.INFO)

load_dotenv()

def is_all_chinese(text: str) -> bool:
    """
    判断字符串是否全部由中文字符 + 中文标点组成
    """
    pattern = re.compile(r'^[\u4e00-\u9fff\u3000-\u303f]+$')
    return bool(pattern.match(text))

def cosine_similarity_manual(vec1, matrix):
    """手动计算余弦相似度"""
    def norm(v):
        return math.sqrt(sum(x*x for x in v))
    
    n1 = norm(vec1)
    if n1 == 0: return [0.0] * len(matrix)
    
    scores = []
    for vec2 in matrix:
        n2 = norm(vec2)
        if n2 == 0:
            scores.append(0.0)
            continue
        dot = sum(a*b for a, b in zip(vec1, vec2))
        scores.append(dot / (n1 * n2))
    return scores

class SimpleTFIDF:
    """手动实现简单的 TF-IDF 向量化器，去除对 sklearn 的依赖"""
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.idf = {}
        self.vocabulary = {}
        self.documents_tfidf = []

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'tokenizer' in state:
            del state['tokenizer']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.tokenizer = None

    def fit_transform\
                    (self, raw_documents):
        # 1. 分词并统计词频
        tf_docs = []
        df_counts = Counter()
        
        for doc in raw_documents:
            tokens = self.tokenizer(doc)
            tf = Counter(tokens)
            tf_docs.append(tf)
            for term in set(tokens):
                df_counts[term] += 1
        
        # 2. 计算 IDF
        num_docs = len(raw_documents)
        self.idf = {term: math.log((1 + num_docs) / (1 + df)) + 1 for term, df in df_counts.items()}
        
        # 3. 构建词汇表
        self.vocabulary = {term: i for i, term in enumerate(sorted(self.idf.keys()))}
        
        # 4. 转换为向量
        self.documents_tfidf = [self._vectorize(tf) for tf in tf_docs]
        return self.documents_tfidf

    def transform(self, raw_documents):
        vectors = []
        for doc in raw_documents:
            tokens = self.tokenizer(doc)
            tf = Counter(tokens)
            vectors.append(self._vectorize(tf))
        return vectors

    def _vectorize(self, tf):
        vector = [0.0] * len(self.vocabulary)
        for term, count in tf.items():
            if term in self.vocabulary:
                idx = self.vocabulary[term]
                vector[idx] = count * self.idf[term]
        return vector

class RAGService():
    def __init__(self):
        self.cache_path = Path("cache")
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # 定义名著配置
        self.books_config = {
            "红楼梦": {"path": "./txt/红楼梦", "pattern": "*.md"},
            "水浒传": {"path": "./txt/水浒传/原文版水浒传", "pattern": "*.html"},
            "西游记": {"path": "./txt/西游记/原文版西游记", "pattern": "*.html"}
        }
        
        # 存储每本书的数据：{book_name: {"texts": [], "vector": [], "vectorizer": None}}
        self.books_data = {}
        self.tokenizer = jieba.lcut
        
        # 对话历史：存储格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        self.chat_history = []
        self.max_history_len = 10  # 保持最近 5 轮对话（10 条消息）
        
        # class初始化
        self.init()

    def clear_history(self):
        """清空对话历史"""
        self.chat_history = []

    def load_cache(self, book_name):
        chunks_dir = self.cache_path / f"{book_name}_chunks.pkl"
        vectors_dir = self.cache_path / f"{book_name}_vectors.pkl"
        vectorizer_dir = self.cache_path / f"{book_name}_vectorizer.pkl"
        
        if chunks_dir.exists() and vectors_dir.exists() and vectorizer_dir.exists():
            print(f"正在从缓存加载 {book_name}...")
            with open(chunks_dir, "rb") as f:
                texts = pickle.load(f)
            with open(vectors_dir, "rb") as f:
                vector = pickle.load(f)
            with open(vectorizer_dir, "rb") as f:
                vectorizer = pickle.load(f)
            
            # 恢复 tokenizer
            vectorizer.tokenizer = self.tokenizer
            
            self.books_data[book_name] = {
                "texts": texts,
                "vector": vector,
                "vectorizer": vectorizer
            }
            return True
        return False

    def extract_content(self, file_path):
        suffix = file_path.suffix.lower()
        if suffix == '.md':
            return self.extract_md_section(file_path)
        elif suffix == '.html':
            return self.extract_html_section(file_path)
        return '', ''

    def extract_html_section(self, file_path):
        """处理 HTML 格式的文本（水浒传、西游记）"""
        try:
            text = Path(file_path).read_text(encoding='utf-8')
            # 提取 <h1> 标签内的标题
            title_match = re.search(r'<h1>(.*?)<span', text)
            if not title_match:
                title_match = re.search(r'<h1>(.*?)</h1>', text)
            title = title_match.group(1).strip() if title_match else file_path.stem
            
            # 提取正文（<p> 标签内的内容）
            # 简单的正则提取，过滤 HTML 标签
            body_parts = re.findall(r'<p>(.*?)</p>', text, re.DOTALL)
            body = "\n".join(body_parts)
            body = re.sub(r'<[^>]+>', '', body) # 过滤所有内部标签
            body = body.replace('&nbsp;', ' ').strip()
            
            return title, body
        except Exception as e:
            print(f"解析 HTML 出错 {file_path}: {e}")
            return '', ''

    def extract_md_section(self, file_path):
        # 保持原有的 md 提取逻辑
        text = Path(file_path).read_text(encoding='utf-8')
        title_match = re.search(r'^###\s+(.+)$', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ''
        if not title_match: return title, ''
        pos = title_match.end()
        sep_pattern = re.compile(r'\n[-—]{3,}\s*\n')
        sep_match = sep_pattern.search(text, pos)
        if sep_match and sep_match.start() == pos: pos = sep_match.end()
        next_sep = sep_pattern.search(text, pos)
        end = next_sep.start() if next_sep else len(text)
        content = text[pos:end].strip()
        content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]*`', '', content)
        content = content.replace('&nbsp;', ' ').replace('\u00A0', ' ').replace('&quot', ' ').replace('<br>', ' ')
        content = re.sub(r' +', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content).strip()
        return title, content

    def init_book(self, book_name):
        config = self.books_config[book_name]
        pattern = Path(config["path"]).rglob(config["pattern"])
        
        # 按文件名排序
        def get_sort_key(p):
            # 尝试提取数字
            nums = re.findall(r'\d+', p.stem)
            return int(nums[0]) if nums else p.stem

        files = sorted(pattern, key=get_sort_key)
        book_texts = []
        
        print(f"正在处理名著：{book_name}...")
        for file in files:
            title, body = self.extract_content(file)
            if title and body:
                book_texts.append({'title': f"《{book_name}》{title}", 'body': body})
        
        if not book_texts:
            print(f"警告：未找到 {book_name} 的有效内容。")
            return

        # 向量化
        print(f"正在为 {book_name} 计算 TF-IDF 向量...")
        tv = SimpleTFIDF(tokenizer=self.tokenizer)
        bodies = [x["body"] for x in book_texts]
        vectors = tv.fit_transform(bodies)
        
        self.books_data[book_name] = {
            "texts": book_texts,
            "vector": vectors,
            "vectorizer": tv
        }
        
        # 缓存
        with open(self.cache_path / f"{book_name}_chunks.pkl", "wb") as f:
            pickle.dump(book_texts, f)
        with open(self.cache_path / f"{book_name}_vectors.pkl", "wb") as f:
            pickle.dump(vectors, f)
        with open(self.cache_path / f"{book_name}_vectorizer.pkl", "wb") as f:
            pickle.dump(tv, f)
        
        print(f"{book_name} 加载并索引完成。")

    def init(self):
        for book_name in self.books_config:
            if not self.load_cache(book_name):
                self.init_book(book_name)

    def identify_book(self, query):
        """识别用户问题涉及哪本名著"""
        # 简单的关键词识别
        keywords = {
            "红楼梦": ["红楼", "黛玉", "宝玉", "宝钗", "贾府", "大观园", "金陵十二钗"],
            "水浒传": ["水浒", "宋江", "林冲", "武松", "鲁智深", "梁山", "好汉", "高俅"],
            "西游记": ["西游", "悟空", "唐僧", "八戒", "沙僧", "大圣", "取经", "妖怪", "如来"]
        }
        
        for book, keys in keywords.items():
            for key in keys:
                if key in query:
                    return book
        
        # 如果关键词没匹配到，通过 LLM 识别
        print("正在分析问题涉及的名著种类...")
        prompt = f"请分析以下用户问题涉及中国四大名著中的哪一本（红楼梦、水浒传、西游记）。仅输出名著名称，如果无法确定则输出'未知'。\n问题：{query}"
        
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        model = "deepseek-v4-flash"
        
        try:
            session = requests.Session()
            session.trust_env = False
            response = session.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                },
                timeout=10
            )
            res = response.json()["choices"][0]["message"]["content"].strip()
            for book in self.books_config:
                if book in res: return book
        except:
            pass
            
        return "红楼梦" # 默认

    def query_documents(self, query: str, book_name: str, top_n: int = 5):
        data = self.books_data.get(book_name)
        if not data: return []
        
        vectorizer = data["vectorizer"]
        hlm_vector = data["vector"]
        hlm_texts = data["texts"]
        
        query_vector = vectorizer.transform([query])[0]
        similarities = cosine_similarity_manual(query_vector, hlm_vector)
        
        indexed_similarities = list(enumerate(similarities))
        top_indices = sorted(indexed_similarities, key=lambda x: x[1], reverse=True)[:top_n]
        
        retrieved_results = []
        for i, score in top_indices:
            retrieved_results.append({
                "chunk": hlm_texts[i],
                "score": float(score)
            })
        return retrieved_results

    def answer_question_with_llm(self, query: str, retrieved_results: list) -> tuple[str, list[str]]:
        context = "\n\n".join([item["chunk"]["body"] for item in retrieved_results])
        
        # 构建当前问题的提示词
        current_prompt = f"根据以下信息回答问题：\n\n{context}\n\n问题：{query}\n\n请注意，如果信息中没有提及，请不要凭空捏造答案。然后以该问题的专业人事的口吻回答问题"

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1")
        model = os.getenv("AI_MODEL", "deepseek-chat")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # 组装消息列表：系统提示词 + 历史对话 + 当前问题
        messages = [{"role": "system", "content": "你是一个基于文档的问答助手，请根据提供的文档内容回答问题。"}]
        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": current_prompt})

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.3,
        }

        print("正在调用大模型生成回答...")
        
        # 尝试使用 requests 调用，并彻底禁用环境代理
        session = requests.Session()
        session.trust_env = False  # 忽略系统环境变量中的代理设置
        
        try:
            response = session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"]
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": llm_response})
            
            # 限制历史长度
            if len(self.chat_history) > self.max_history_len:
                self.chat_history = self.chat_history[-self.max_history_len:]
                
        except Exception as e:
            error_msg = f"网络请求失败: {str(e)}"
            print(error_msg)
            return error_msg, []
        
        # 提取标题和分数的去重列表
        seen_titles = set()
        source_info = []
        for item in retrieved_results:
            title = item["chunk"]["title"]
            score = item["score"]
            if title not in seen_titles:
                source_info.append(f"{title} (相似度: {score:.4f})")
                seen_titles.add(title)

        return llm_response, source_info


if __name__ == '__main__':
    print("\n" + "="*50)
    print("正在启动多名著 RAG 智能问答系统...")
    print("="*50)
    
    rag_service = RAGService()
    
    print("\n系统已就绪！支持《红楼梦》、《水浒传》、《西游记》。")
    print("输入 'exit' 或 'quit' 退出系统，输入 'clear' 清空对话记忆。")
    
    while True:
        print("\n" + "-"*50)
        query = input("用户问题: ").strip()
        
        if not query:
            continue
            
        if query.lower() in ['exit', 'quit']:
            print("感谢使用，再见！")
            break
            
        if query.lower() == 'clear':
            rag_service.clear_history()
            print("对话记忆已清空。")
            continue
            
        try:
            # 0. 识别名著
            book_name = rag_service.identify_book(query)
            print(f"识别到相关名著：{book_name}")
            
            # 1. 检索文档
            print(f"正在检索《{book_name}》相关内容...")
            retrieved_results = rag_service.query_documents(query, book_name, top_n=5)
            
            if not retrieved_results:
                print(f"未在《{book_name}》中找到相关内容。")
                continue
                
            print(f"检索到最相关的章节：")
            for item in retrieved_results:
                print(f"- {item['chunk']['title']} (相似度: {item['score']:.4f})")
            
            # 2. 调用大模型
            answer, sources = rag_service.answer_question_with_llm(query, retrieved_results)
            
            # 3. 输出结果
            print("\n" + "*"*20 + " 模型回答 " + "*"*20)
            print(answer)
            print("*"*50)
            
            if sources:
                print(f"\n参考文档: {', '.join(sources)}")
                
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print("请尝试重新输入或检查网络连接。")
