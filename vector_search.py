from gradio_client import Client
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from mongo import summary_collection
from resources import  cycu_resources  # 從 resources.py 匯入
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

def query_vectorstore(text, user_id, threshold=0.35):
    """
    回傳整合文字：
    - 最相關資源 + 個人摘要
    - 或 用途索引 + 個人摘要
    """
    # 只計算一次向量
    query_emb = embeddings.embed_query(text)

    # --- 查 FAISS ---
    results_faiss = vectorstore.similarity_search_with_score_by_vector(query_emb, k=1)
    faiss_hit = False
    if results_faiss:
        top_doc, top_score = results_faiss[0]
        if top_score <= threshold:
            faiss_hit = True
            doc_content = top_doc.page_content
        else:
            doc_content = None
    else:
        doc_content = None

    # --- 查 MongoDB summary ---
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": query_emb,
                "path": "embedding",
                "index": "sum",
                "k": 1,
                "numCandidates": 100,
                "filter": {"user_id": user_id},
                "limit": 1
            }
        }
    ]
    results_sum = list(summary_collection.aggregate(pipeline))
    summary = results_sum[0].get("summary", "") if results_sum else ""

    # --- 組合文字輸出 ---
    if faiss_hit:
        output = f"以下是與您問題最相關的學校資源：\n{doc_content}"
    else:
        usage_index = json.dumps(cycu_resources.get('用途索引', {}), ensure_ascii=False)
        output = f"以下是可參考的學校資源索引：\n{usage_index}"

    if summary:
        output += f"以下是最相關的歷史摘要：\n{summary}"

    return output