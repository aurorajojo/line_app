# cycu_faiss_index

## 介紹
`cycu_faiss_index` 是一個使用 **[intfloat/multilingual-e5-large](https://huggingface.co/intfloat/multilingual-e5-large)** 模型產生的向量資料庫，內容為中原大學各項資源的文字描述，包含藝文資源、學習資源、心理輔導、體育場館、餐飲、教官室等資訊。

本向量資料庫可用於語意檢索，讓使用者以自然語言查詢，例如：
> 「游泳池幾點開？」  
系統會回傳對應的資訊與向量距離。

## 向量生成
本資料庫的向量是使用 **intfloat/multilingual-e5-large** 模型生成，建立過程：
1. 將 `cycu_resources.txt` 依空行分段切割成 chunk
2. 使用 `intfloat/multilingual-e5-large` 對每個 chunk 產生向量
3. 使用 [FAISS](https://github.com/facebookresearch/faiss) 建立索引，並儲存為 `cycu_faiss_index` 資料夾

## 查詢方式
vector_search.py 將透過本人架設的 Hugging Face Space：
[https://huggingface.co/spaces/aurorajojo/e5-large-embedding-api](https://huggingface.co/spaces/aurorajojo/e5-large-embedding-api) 去查詢

使用流程：
1. 使用 Hugging Face `gradio_client` 呼叫 API
2. API 回傳查詢文字的向量
3. 與 `cycu_faiss_index` 中的向量比對
4. 回傳最相似的文件內容與向量距離

## 📂 資料夾內容

| 檔案名稱             | 說明 |
|----------------------|------|
| `index.faiss`        | FAISS 的主索引檔，儲存所有向量與索引結構 |
| `index.pkl`          | 對應向量的原始文本與中繼資料（metadata）序列化檔 |


---

## 📖 資料來源

此索引是由 `cycu_resources.txt` 建立，該檔案內容包含：
- **藝文資源**（音樂廳、藝術中心等）
- **學習資源**（圖書館、自學空間、討論室等）
- **心理輔導資源**（諮商中心、心理治療所等）
- **職涯發展**（職涯發展處、學用區等）
- **體育設施**（游泳池、體育館、球場等）
- **餐飲資源**（星巴克、路易莎、麥當勞等）
- **教官室**（各系所教官與聯絡方式）

---

