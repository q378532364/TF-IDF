
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

model = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key="sk-1083b6b87898441dbce4e69add10aea6",
    # DeepSeek 的 API 兼容 OpenAI 接口格式，但需要指定其专属 base_url
    base_url="https://api.deepseek.com"
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """  
    你是一个问答助手，你要很有礼貌的回答用户提问的问题。
    """),
    MessagesPlaceholder(variable_name="messages"),
])

# 迁移说明：
# 原来使用 langchain_community.ChatMessageHistory + RunnableWithMessageHistory 的方案已废弃
# 改用 LangGraph 内置持久化（MemorySaver），自动管理消息历史，无需手动维护 store 字典
# MemorySaver 是内存级 checkpointer，按 thread_id（即 session_id）自动存取消息历史
checkpointer = MemorySaver()

def chatbot(state: MessagesState):
    # 从 state["messages"] 中拿到历史消息 + 当前用户输入
    # prompt_template 只需要 system 部分，MessagesPlaceholder 会注入完整历史
    # LangGraph 自动将所有消息（含 AI 回复）存入 checkpointer
    response = model.invoke(prompt_template.invoke({"messages": state["messages"]}))
    return {"messages": [response]}

# 构建 LangGraph 状态图：chatbot 节点接收消息状态，返回更新后的消息
graph = StateGraph(MessagesState)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# compile 时传入 checkpointer，使图具备持久化能力
app = graph.compile(checkpointer=checkpointer)

# config 中的 thread_id 相当于原来的 session_id，用于隔离不同用户的聊天历史
config = {"configurable": {"thread_id": "customer_zhangsan"}}

print("=== 智能客服已上线 ===")


def chat(user_input: str):

    print("> " + user_input)
    print("AI: ", end="", flush=True)
    # stream_mode="messages" 返回 (AIMessageChunk, metadata) 元组
    # 每个 chunk 是增量内容，拼接起来就是完整回复
    for chunk, _ in app.stream(
        {"messages": [("user", user_input)]},
        config=config,
        stream_mode="messages",
    ):
        # 过滤掉非 AI 消息的 chunk（如 tool call 等），只打印文本内容
        if chunk.content and isinstance(chunk.content, str):
            print(chunk.content, end="", flush=True)
    print()  # 换行


def chat2(user_input: str):
    """直接输出：等待 AI 完整回复后一次性打印"""
    print("> " + user_input)
    resp = app.invoke(
        {"messages": [("user", user_input)]},
        config=config,
    )
    print(f"AI: {resp['messages'][-1].content}")
if __name__ == "__main__":
    pass

#
# chat("我最喜欢的是苹果")
# chat("你记不记得我刚才说不喜欢什么？")

# print("\n--- 直接输出模式 ---\n")
#
# chat2("我最讨厌的是香蕉")
# chat2("你记得我刚才说什么了？")
