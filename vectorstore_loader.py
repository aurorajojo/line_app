# vectorstore_loader.py
"""
這個模組專門負責「載入已建立好的 FAISS 向量資料庫」，
並返回一個 vectorstore 物件供其他程式呼叫。
使用 LangChain 的 HuggingFaceEmbeddings 來做文字向量化，
向量資料庫使用 FAISS（Facebook AI Similarity Search）。
"""

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import torch

def load_vectorstore(
    index_path: str = "cycu_faiss_index",              # 向量庫資料夾路徑
    model_name: str = "intfloat/multilingual-e5-base", # 預設使用的 Embedding 模型名稱
    use_gpu_if_available: bool = True                  # 是否在有 GPU 時使用 GPU
):
    # 判斷要使用 CPU 還是 GPU
    device = "cuda" if torch.cuda.is_available() and use_gpu_if_available else "cpu"
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,                       #指定模型名稱
        model_kwargs={"device": device},             #指定 device（"cuda" 或 "cpu"）
        encode_kwargs={"normalize_embeddings": True} #讓向量在生成後自動 L2 正規化，方便使用 Cosine Similarity 計算相似度
    )
    vectorstore = FAISS.load_local(
        index_path,                             #向量庫所在資料夾
        embeddings,                             #載入向量庫時需要同樣的 Embedding 模型
        allow_dangerous_deserialization=True    #允許從本地檔案反序列化（必要，否則會報安全警告）
    )

    # 回傳向量庫物件，供外部直接使用
    return vectorstore

