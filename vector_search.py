# vector_search.py
# 當 cycu_resources 有相關資料：回傳「最相關的學校資源」+（若有的話）「歷史摘要」最多兩筆。  
# 當 cycu_resources 無相關資料：回傳「用途索引」+（若有的話）「歷史摘要」最多兩筆。 

from gradio_client import Client
from langchain_core.embeddings import Embeddings
from mongo import summary_collection
from resources import  cycu_resources  # 從 resources.py 匯入
import json
import re

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


def query_vectorstore(text, user_id, threshold=0.35):
    """
    回傳學校資源資訊或用途索引，並附個人歷史摘要最多兩筆：
    - 最相關資源 + 個人摘要
    - 或 
    - 用途索引 + 個人摘要
    """
    text_lower = text.lower()
    matched_resource = None

    for res_name in cycu_resources.get("中原大學資源", {}):
        # 忽略大小寫模糊比對（substring match）
        if re.search(re.escape(res_name.lower()), text_lower):
            matched_resource = res_name
            break

    # 只計算一次向量
    query_emb = embeddings.embed_query(text)

    # --- 查 MongoDB summary ---
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": query_emb,
                "path": "embedding",
                "index": "sum",
                "k": 2,
                "numCandidates": 100,
                "filter": {"user_id": user_id},
                "limit": 2
            }
        }
    ]
    results_sum = list(summary_collection.aggregate(pipeline))
    summary_list = [res.get("summary", "") for res in results_sum]
    summary_text = "\n---\n".join(summary_list) if summary_list else ""


    # --- 組合文字輸出 ---
    if matched_resource:
        # 回傳完整資源資訊
        resource_info = cycu_resources["中原大學資源"].get(matched_resource, {})
        output = (
            f"以下是與您問題相關的學校資源：\n"
            f"{matched_resource}：\n"
            f"{json.dumps(resource_info, ensure_ascii=False)}"
        )
    else:
        # 回傳用途索引
        usage_index = json.dumps(cycu_resources.get("用途索引", {}), ensure_ascii=False)
        output = f"以下是可參考的學校資源索引：\n{usage_index}"

    # 附上歷史摘要（RAG）
    if summary_text:
        output += f"\n以下是最相關的歷史摘要：\n{summary_text}"

    return output