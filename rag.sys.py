import sys
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path


class RAGService():
    def __init__(self):

        # 红楼梦文本
        self.hlm_texts=[]
        # 红楼梦向量
        self.hlm_vector=[]
        # class初始化
        self.init()

    def extract_md_section(self,file_path):

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
        temp=Path("txt/红楼梦").rglob("*.md")
        for file in list(temp):
            title,body =  self.extract_md_section(file)
            currentText=''
            tempList=re.split(r'\n', body)
            index=0
            for item in tempList:
                if(len(item)+ len(currentText)<300):
                    currentText+=item
                else:
                    self.hlm_texts.append({'title':f"{title}[{index}]",'body':currentText})
                    index+=1
                    currentText+=item+'\n'

        print(len(self.hlm_texts))

    def int_docVect(self):
        pass



    def init(self):
        # 加载文档
        self.init_doc()
        pass



if __name__ == '__main__':
     RAGService()


    
