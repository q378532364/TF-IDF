import sys
import re
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
import jieba


class RAGService():
    def __init__(self):

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
        pattern = Path("txt/红楼梦").rglob("*.md")

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

    def tokenizer(self):
        pass

    def int_docVect(self):
        word_list = jieba.cut("我来自北京大学", cut_all=False)
        print(",".join(word_list))
        tv = TfidfVectorizer(
            tokenizer=self.tokenizer,
            max_features=5000,  # 能取到最大特征值
            min_df=2,  # 忽略出现少于2次的词
            max_df=0.95,  # 忽略出现概率大于95%以上的词
            ngram_range=(1, 2),  # 包含1～2个词的选择
        )

        texts = [x["body"] for x in self.hlm_texts]
        tv.fit_transform(texts)



    def init(self):
        # 加载文档
        self.init_doc()
        self.int_docVect()


if __name__ == '__main__':
    RAGService()
