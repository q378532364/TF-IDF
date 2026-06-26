from  langgraph.graph import  MessagesState


from langchain_openai import  ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import  StateGraph,START,END
from langgraph.checkpoint.memory import  MemorySaver

config = {"configurable": {"thread_id": "demo2_session"}}

model=ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key="sk-1083b6b87898441dbce4e69add10aea6"
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system","你是一个很有礼貌的助手。"),
    MessagesPlaceholder(variable_name="messages")
])

def chatbot(state:MessagesState):
    current_message = state["messages"]
    prompt=prompt_template.invoke({"messages":current_message})
    response=model.invoke(prompt)
    return  {"messages":[response]}


workflow=StateGraph(MessagesState)

workflow.add_node("chatbot_node",chatbot)


workflow.add_edge(START,"chatbot_node")
workflow.add_edge("chatbot_node",END)

memory=MemorySaver()

app=workflow.compile(checkpointer=memory)


def ask_bot(user_input:str):

    print("AI: ", end="", flush=True)
    for chunk, _ in app.stream(
        {"messages": [("user", user_input)]},
        config=config,
        stream_mode="messages",
    ):
        if chunk.content and isinstance(chunk.content, str):
            print(chunk.content, end="", flush=True)
    print()

if __name__=="__main__":
    print("="*5+"欢迎来到AI助手"+"="*5)
    while True:
        str1= str(input("> "))
        ask_bot(str1)







