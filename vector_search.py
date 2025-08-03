from gradio_client import Client
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import json

HF_SPACE_ID = "aurorajojo/e5-large-embedding-api"
HF_API_NAME = "/predict"

client = Client(HF_SPACE_ID)

class APIEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [client.predict(t, api_name=HF_API_NAME)[0] for t in texts]
    def embed_query(self, text):
        return client.predict(text, api_name=HF_API_NAME)[0]

# 載入本地向量庫資料夾
embeddings = APIEmbeddings()
vectorstore = FAISS.load_local(
    "cycu_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# 你自己的用途索引
with open("cycu_resources.json", "r", encoding="utf-8") as f:
    cycu_resources = json.load(f)

def query_vectorstore(text, top_k=1, threshold=0.75):
    """
    傳入查詢字串 text，回傳：
    - 是否有超過 threshold 的相似度
    - 若有，回傳最相似的文件內容與相似度
    - 若無，回傳用途索引（字串）
    """
    results = vectorstore.similarity_search_with_score(text, k=top_k)
    if results:
        top_doc, top_score = results[0]
        if top_score >= threshold:
            return True, top_doc.page_content, top_score                    #回傳最相似的文件內容與相似度
    usage_index = json.dumps(cycu_resources.get("用途索引", {}), ensure_ascii=False)
    return False, usage_index, None     #回傳用途索引（字串）
