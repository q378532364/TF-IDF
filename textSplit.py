from langchain_text_splitters import  MarkdownHeaderTextSplitter
lan
markdown_document = """
# 🍅 西红柿种植技术
## 二、病虫害防治
### 1. 晚疫病
如果发现叶片出现水渍状暗绿色病斑，应立即使用百菌清进行喷洒。
"""

headers_to_split_on = [
    ("#", "header_1"),
    ("##", "header_2"),
    ("###", "header_3"),
]

markdown_splitter=MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits=markdown_splitter.split_text(markdown_document)

for chunk in md_header_splits:
    print(chunk)