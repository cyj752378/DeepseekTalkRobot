# 导入 langchain集成的 DeepSeek 聊天模型
from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(model="deepseek-chat",  # 模型名称，deepseek-chat: 大模型
                   temperature=0.5,  # 控制输出随机性的参数，0.0-1.0之间，
                   api_key="sk-2243f549cd3f4680ae3682ea355eb90e")

messages = [
    {"role": "system", "content": "你是一个有帮助的AI助手。"},  # 系统设置
    {"role": "user", "content": "畅享一下未来AI的发展前景"}  # 你的问题
]
response = llm.invoke(messages)

print(response.content)