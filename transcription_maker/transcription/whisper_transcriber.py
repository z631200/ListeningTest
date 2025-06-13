import whisper
from tqdm import tqdm
# from utils.time_utils import format_time
# from config import SEGMENT_LEN_MS
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_file")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 確保輸出目錄存在

def format_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02}:{mins:02}:{secs:02}"
def transcribe_with_original_time(mp3_path, segment_offset_map):
    model = whisper.load_model("base")

    print("🔍 載入音訊並準備轉錄...")
    audio = whisper.load_audio(mp3_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    print("🧠 開始轉錄 + 進度顯示...\n")
    options = whisper.DecodingOptions(language="en")
    segments = []

    # 使用 tqdm 包裝進度條
    result = model.transcribe(mp3_path, language="en", verbose=False)
    total = len(result["segments"])

    for seg in tqdm(result["segments"], desc="🔄 Whisper 轉錄中", unit="段"):
        segments.append(seg)

    # 呼叫映射邏輯
    map_whisper_segments_to_original({"segments": segments}, segment_offset_map)


def map_whisper_segments_to_original(result, segment_offset_map):
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02}:{secs:02}"

    mapped_segments = []

    for seg in result["segments"]:
        new_start_ms = int(seg["start"] * 1000)

        match = None
        for m in segment_offset_map:
            if m["new_start_ms"] <= new_start_ms < m["new_end_ms"]:
                match = m
                break

        if not match:
            continue

        offset = new_start_ms - match["new_start_ms"]
        original_start = (match["original_start_ms"] + offset) / 1000
        original_end = original_start + (seg["end"] - seg["start"])

        mapped_segments.append({
            "original_start": original_start,
            "original_end": original_end,
            "text": seg["text"]
        })

    # ✅ 按照「原始時間」排序
    mapped_segments.sort(key=lambda x: x["original_start"])

    # 生成輸出檔案名稱（使用時間戳記）
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_file = f"transcription_{timestamp}.txt"
    output_file = os.path.join(OUTPUT_DIR, "transcription.txt")

    show_transcription = input("是否顯示轉錄結果？(y/n)：").lower()
    with open(output_file, "w", encoding="utf-8") as f:
        if show_transcription == "y":    
            print("📋 含【原始音訊時間】的轉錄結果如下（已排序）：\n")
        
        for seg in mapped_segments:
            start_str = format_time(seg["original_start"])
            end_str = format_time(seg["original_end"])
            line = f"[原始時間 {start_str} - {end_str}] {seg['text']}"
            
            if show_transcription == "y":
                print(line)  # 輸出到終端機
                
            f.write(line + "\n")  # 寫入檔案

    print(f"\n📋 轉錄結果已保存至：{output_file}")
