# hf_vector_api.py
import re
import json
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from gradio_client import Client

# HF Space API 設定
HF_SPACE_ID = "aurorajojo/e5-large-embedding-api"
HF_API_NAME = "/predict"
client = Client(HF_SPACE_ID)

# 封裝 Hugging Face API Embeddings
class APIEmbeddings:
    def embed_documents(self, texts):
        # 每個文本都呼叫 API
        embeddings = []
        for t in texts:
            result = client.predict(t, api_name=HF_API_NAME)
            embeddings.append(result[0])  # HF API 回傳 [[float,...]]，取第一個列表
        return embeddings

    def embed_query(self, text):
        result = client.predict(text, api_name=HF_API_NAME)
        return result[0]

embeddings = APIEmbeddings()

# 讀取文字檔
with open("cycu_resources.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 切分段落
paragraphs = re.split(r"\n\s*\n", text)
docs = [Document(page_content=p) for p in paragraphs]

# 切 chunk
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunked_docs = splitter.split_documents(docs)

# 建立 FAISS 向量庫
vectorstore = FAISS.from_documents(chunked_docs, embeddings)
vectorstore.save_local("cycu_faiss_index")

print("✅ 向量資料庫已使用 Hugging Face API 儲存到 cycu_faiss_index")