from config import llm



response = llm.invoke("hello world")
print(response.content)



