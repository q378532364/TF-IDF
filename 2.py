from idlelib import query

import  jieba
from  rank_bm25 import  BM25Okapi
import  glob
from pathlib import  Path


f=Path("./txt")
docs=[]
for file_path in f.glob("*.txt"):
    content=file_path.read_text(encoding="utf-8")
    docs.append(content)

tokens_list=[list(jieba.cut_for_search(doc)) for doc in docs]
print(tokens_list)

query="华123为手机"

tokens_query=list(jieba.cut_for_search(query))
bm25_model = BM25Okapi(tokens_list)
top_docs=bm25_model.get_scores(tokens_query)

print(top_docs)


# print(tokens_list)
