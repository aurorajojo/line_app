# cycu_faiss_index

## 介紹
`cycu_faiss_index` 是一個使用 **[intfloat/multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large)** 模型產生的向量資料庫，內容為中原大學各項資源的文字描述，包含藝文資源、學習資源、心理輔導、體育場館、餐飲、教官室等資訊。

本向量資料庫可用於語意檢索，讓使用者以自然語言查詢，例如：
> 「諮商中心幾點開？」  
系統會回傳對應的資訊與向量距離。再以向量距離判斷是否將對應資訊加入 prompt 。

## 資料庫建立過程

1. 將 `cycu_resources.txt` 依空行分段切割成 chunk
2. 使用 `intfloat/multilingual-e5-large` 模型對每個 chunk 產生向量
3. 使用 FAISS 建立索引，並儲存為 `cycu_faiss_index` 資料夾

## 查詢方式

vector_search.py 使用流程：
1. **向量化**  
   呼叫我們自己架設的Hugging Face Space（[aurorajojo/e5-large-embedding-api](https://huggingface.co/spaces/aurorajojo/e5-large-embedding-api)）將使用者 input 轉換為向量。

2. **載入向量庫**  
   透過 `FAISS.load_local()` 載入本地向量庫 （[cycu_faiss_index](https://github.com/aurorajojo/line_app/blob/main/cycu_faiss_index))。內容為中原大學各項資源的文字描述，包含藝文資源、學習資源、心理輔導、體育場館、餐飲、教官室等資訊。

4. **向量距離比對**  
   `query_vectorstore()` 執行檢索並判斷距離閾值（預設 0.35）：  
   - **符合閾值** → 回傳最相關資訊句子與向量距離分數，以便後續加入prompt回傳給大型語言模型。
   - **不符合** → 回傳 `cycu_resources.json` 中的用途索引，以便後續加入prompt回傳給大型語言模型。
     

## 📂 資料夾內容

| 檔案名稱             | 說明 |
|----------------------|------|
| `index.faiss`        | FAISS 的主索引檔，儲存所有向量與索引結構 |
| `index.pkl`          | 對應向量的原始文本與中繼資料（metadata）序列化檔 |
| `cycu_resources.txt`          | 此索引資料來源，該檔案內容包含：<br> **藝文資源**（音樂廳、藝術中心等）<br> **學習資源**（圖書館、自學空間、討論室等）<br> **心理輔導資源**（諮商中心、心理治療所等）<br> **職涯發展**（職涯發展處、學用區等）<br> **體育設施**（游泳池、體育館、球場等）<br> **餐飲資源**（星巴克、路易莎、麥當勞等）<br> **教官室**（各系所教官與聯絡方式） |

##  intfloat/multilingual-e5-large介紹

-  多語言支援：支援超過 100 種語言（包括中文、英文、日文等），適合中原大學校園中多語查詢情境。
-  語意檢索效果佳：基於微軟提出的 E5 架構（Embedding from Explanation），在各種語意搜尋任務中表現優異。
- 模型架構：基於 BERT 的 Transformer 模型
- 層數：24 層（Large 級別）
- 向量維度：1024 維（每段文字最終會轉換成一個 1024 維的向量）

## 向量距離說明

- 向量距離 是 **查詢向量與資料庫中文檔向量之間的距離分數**，而不是直接的相似度。
- 在本系統使用的 FAISS 向量庫中，距離通常是 **餘弦距離（Cosine Distance）**，計算方式為：  
Cosine Distance = 1 - cosine_similarity
- 向量距離數值介於 0 到 1
- 越接近 0 表示語意越相近。
- 越接近 1 表示語意越相遠。
---
