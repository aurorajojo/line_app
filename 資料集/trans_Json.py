import json
import re
import time
from tqdm import tqdm
from googletrans import Translator

def parse_segment(segment):
    segment = segment.strip()
    if not segment:
        return None
    pattern = r'^(\d+(\.\d+)?)\s+(\d+)\s+(\d+)\s+(?:\[(.*?)\]\s+)?(.+)$'
    match = re.match(pattern, segment)
    if not match:
        return None
    startTag = float(match.group(1))
    speaker = int(match.group(3))
    content_id = int(match.group(4))
    strategy = match.group(5) if match.group(5) else None
    content = match.group(6).strip()
    return {
        "startTag": startTag,
        "speaker": "seeker" if speaker == 0 else "supporter",
        "content_id": content_id,
        "strategy": strategy,
        "content": content
    }

translator = Translator()
translation_cache = {}
failed_sentences = []

input_file = 'trainWithStrategy_short.tsv'
output_file = 'output_dialogues_translated.json'

dialogues = []
current_dialogue = []
previous_startTag = None

with open(input_file, 'r', encoding='utf-8') as f:
    text = f.read()

segments = [seg.strip() for seg in text.split('EOS') if seg.strip()]

for seg in tqdm(segments, desc="🔄 翻譯中", unit="段"):
    parsed = parse_segment(seg)
    if parsed:
        original = parsed["content"]
        if original in translation_cache:
            parsed["content"] = translation_cache[original]
        else:
            try:
                result = translator.translate(original, dest='zh-tw')
                translated = result.text
                parsed["content"] = translated
                translation_cache[original] = translated
                time.sleep(0.3)  # 加入延遲，避免被封鎖
            except Exception as e:
                print(f"⚠️ 翻譯失敗：{original}，錯誤：{e}")
                failed_sentences.append(original)
                parsed["content"] = "[翻譯失敗] " + original

        if parsed['startTag'] == 1.0 and previous_startTag == 0.0:
            if current_dialogue:
                dialogues.append(current_dialogue)
            current_dialogue = [parsed]
        else:
            current_dialogue.append(parsed)

        previous_startTag = parsed['startTag']

if current_dialogue:
    dialogues.append(current_dialogue)

with open(output_file, 'w', encoding='utf-8') as f_out:
    json.dump(dialogues, f_out, ensure_ascii=False, indent=2)

# 額外紀錄失敗句子
if failed_sentences:
    with open('failed_sentences.txt', 'w', encoding='utf-8') as f_fail:
        for sentence in failed_sentences:
            f_fail.write(sentence + '\n')
    print(f"⚠️ 有 {len(failed_sentences)} 句翻譯失敗，已寫入 failed_sentences.txt")

print(f"✅ 完成，共切出 {len(dialogues)} 段對話")
