import pickle
import sys
import re
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
import jieba

def is_all_chinese(text: str) -> bool:
    """
    判断字符串是否全部由中文字符 + 中文标点组成
    中文标点范围：\u3000-\u303f（如：，。！？；：“”‘’…）
    汉字范围：\u4e00-\u9fff + 扩展区域（可选，如需增加可自行添加）
    """
    # 汉字基本区 + 中文标点
    pattern = re.compile(r'^[\u4e00-\u9fff\u3000-\u303f]+$')
    return bool(pattern.match(text))

class RAGService():
    def __init__(self):
        self.cache_path = Path("cache")
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.chunks_dir=self.cache_path/ "hlm_chunks.pkl"
        self.vectors_dir=self.cache_path / "hlm_vectors.pkl"
        # 红楼梦文本
        self.hlm_texts = []
        # 红楼梦向量
        self.hlm_vector = []
        # class初始化
        self.init()

    def extract_md_section(self, file_path):

        text = Path(file_path).read_text(encoding='utf-8')
        # 1. 提取标题（### 开头）
        title_match = re.search(r'^###\s+(.+)$', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ''

        if not title_match:
            return title, ''

        # 2. 跳过标题后的分隔线（如 ---- 或 ————）
        pos = title_match.end()
        sep_pattern = re.compile(r'\n[-—]{3,}\s*\n')
        sep_match = sep_pattern.search(text, pos)
        if sep_match and sep_match.start() == pos:
            pos = sep_match.end()

        # 3. 内容结束位置（下一个分隔线或文件末尾）
        next_sep = sep_pattern.search(text, pos)
        end = next_sep.start() if next_sep else len(text)
        content = text[pos:end].strip()

        # 4. 去除批注（```...``` 或 `...` 中的内容）
        content = re.sub(r'```[^`]*```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]*`', '', content)

        # 5. 去除 &nbsp; 实体 和 Unicode 不间断空格
        content = content.replace('&nbsp;', ' ')  # HTML 实体替换为普通空格
        content = content.replace('\u00A0', ' ')  # 不间断空格替换为普通空格
        content = content.replace('&quot', ' ')  # HTML 实体替换为普通空格
        content = content.replace('<br>', ' ')

        # 可选：连续空格合并为一个空格

        content = re.sub(r' +', ' ', content)

        # 6. 清理多余空行
        content = re.sub(r'\n\s*\n', '\n\n', content).strip()

        return title, content

    def init_doc(self):
        # 获取所有 .md 文件
        pattern = Path("./txt/红楼梦").rglob("*.md")

        # 按文件名中的数字升序排序
        files = sorted(pattern, key=lambda p: int(p.stem))
        for file in list(files):
            title, body = self.extract_md_section(file)

            currentText = ''
            tempList = re.split(r'\n', body)
            index = 0
            for item in tempList:
                if currentText == '':
                    currentText = item
                elif (len(item) + len(currentText) < 300):
                    currentText += item
                elif currentText == '':
                    continue
                else:
                    self.hlm_texts.append({'title': f"{title}[{index}]", 'body': currentText})
                    index += 1
                    currentText += item + '\n'
            print(f"文档分片完成，共生成{len(self.hlm_texts)}")
            with open(self.chunks_dir,"wb") as f:
                f.write(pickle.dumps(self.hlm_texts))

    def tokenizer(self,text):
        tokensData=[]
        for line in jieba.cut(text):
            line=line.strip()
            if is_all_chinese(line):
                # 不是语气词
                # PARTICLE_SET = {
                #         '啊', '哦', '噢', '喔', '呀', '哟', '呦', '哇', '啦', '咧', '咯', '喽', '嘛', '呗',
                #         '呵', '嘿', '哈', '哎', '唉', '诶', '欸', '嗯', '唔', '呕', '呃', '呸', '呲', '哼',
                #         '嚯', '嘘', '喂', '嗨', '哈哈', '呵呵', '嘿嘿', '哎呀', '哎哟', '哇塞', '好嘛', '罢了',
                #         '而已', '也罢', '好了', '就是', '似的', '一样', '的说', '嗯哼', '啊哈', '哦吼', '哎嗨', '嚯嚯'
                # }
                # if line not in PARTICLE_SET:
                tokensData.append(line)
        return tokensData


    def int_docVect(self):
            print("分词中....")
            tv = TfidfVectorizer(
                tokenizer=self.tokenizer,
                max_features=5000,  # 能取到最大特征值
                min_df=2,  # 忽略出现少于2次的词
                max_df=0.95,  # 忽略出现概率大于95%以上的词
                ngram_range=(1, 2),  # 包含1～2个词的选择
            )
            print("分词结束....")
            texts = [x["body"] for x in self.hlm_texts]
            tv.fit_transform(texts)



    def init(self):
        # 加载文档
        self.init_doc()
        self.int_docVect()


if __name__ == '__main__':
    RAGService()
