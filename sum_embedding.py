from pymongo import MongoClient
from gradio_client import Client
from langchain_core.embeddings import Embeddings
from mongo import summary_collection


# 初始化 embedding API
client = Client("aurorajojo/e5-large-embedding-api")

# 自訂 embeddings wrapper
class APIEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [client.predict(t, api_name="/predict")[0] for t in texts]

    def embed_query(self, text):
        return client.predict(text, api_name="/predict")[0]

embeddings = APIEmbeddings()

# 批次更新所有 summary
for doc in summary_collection.find({"embedding": {"$exists": False}}):
    summary_text = doc.get("summary", "")
    if not summary_text:
        continue

    # 產生 embedding
    embedding = embeddings.embed_query(summary_text)

    # 更新資料庫
    summary_collection.update_one(
        {"_id": doc["_id"]},
        {"$set": {"embedding": embedding}}
    )

print("已經幫所有 summary 生成並存好 embedding！")
