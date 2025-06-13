from .downloader.audio_downloader import download_audio
from .audio_processing.segmenter import split_audio
from .audio_processing.sampler import sample_segments, process_full_audio
from .transcription.whisper_transcriber import transcribe_with_original_time
import os
import sys
import glob

# 設定 tool/ 路徑進 PATH，讓 whisper 可以呼叫 ffmpeg
tool_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tool"))
os.environ["PATH"] = f"{tool_dir};{os.environ['PATH']}"

def process_local_audio(audio_path: str, use_sampling: bool = True):
    """處理本地音訊檔案"""
    if not os.path.exists(audio_path):
        print(f"❌ 找不到音訊檔案：{audio_path}")
        return

    # [1] 切割音訊
    segments, duration_ms = split_audio(audio_path)
    print("[1] 音訊切割完成")

    # [2] 處理音訊（抽樣或完整）
    if use_sampling:
        print("[2] 開始音訊抽樣...")
        sampled_path, segment_offset_map = sample_segments(segments, duration_ms)
    else:
        print("[2] 開始處理完整音訊...")
        sampled_path, segment_offset_map = process_full_audio(segments, duration_ms)
    print("[2] 音訊處理完成")

    # [3] Whisper 轉錄 + 回推原始時間
    print("[3] 開始 Whisper 轉錄...")
    transcribe_with_original_time(sampled_path, segment_offset_map)

def process_youtube_video(use_sampling: bool = True):
    """處理 YouTube 影片"""
    youtube_url = input("請輸入 YouTube 影片網址：")

    # [1] 下載音訊
    audio_path = download_audio(youtube_url)
    print("[1] 音訊下載完成")

    # [2] 切割音訊
    segments, duration_ms = split_audio(audio_path)

    # [3] 處理音訊（抽樣或完整）
    if use_sampling:
        print("[2] 開始音訊抽樣...")
        sampled_path, segment_offset_map = sample_segments(segments, duration_ms)
    else:
        print("[2] 開始處理完整音訊...")
        sampled_path, segment_offset_map = process_full_audio(segments, duration_ms)
    print("[2] 音訊處理完成")

    # [4] Whisper 轉錄 + 回推原始時間
    print("[3] 開始 Whisper 轉錄...")
    transcribe_with_original_time(sampled_path, segment_offset_map)

def delete_files_in_directory():
    extensions = ["*.wav", "*.mp3", "*.txt"]
    deleted_files = []
    for ext in extensions:
        for file in glob.glob(ext):
            try:
                os.remove(file)
                deleted_files.append(file)
            except Exception as e:
                print(f"⚠️ 無法刪除 {file}：{e}")
    if deleted_files:
        print("✅ 已刪除以下檔案：")
        for f in deleted_files:
            print(f" - {f}")
    else:
        print("📂 沒有找到任何 wav、mp3 或 txt 檔案。")

def quiz_maker():
    return

def test_func():
    use_sampling = True
    # [1] 下載音訊
    audio_path = download_audio("https://www.youtube.com/watch?v=N02AZF_v5ZU")
    print("[1] 音訊下載完成")

    # [2] 切割音訊
    segments, duration_ms = split_audio(audio_path)

    # [3] 處理音訊（抽樣或完整）
    if use_sampling:
        print("[2] 開始音訊抽樣...")
        sampled_path, segment_offset_map = sample_segments(segments, duration_ms)
    else:
        print("[2] 開始處理完整音訊...")
        sampled_path, segment_offset_map = process_full_audio(segments, duration_ms)
    print("[2] 音訊處理完成")

    # [4] Whisper 轉錄 + 回推原始時間
    print("[3] 開始 Whisper 轉錄...")
    transcribe_with_original_time(sampled_path, segment_offset_map)

def core():
    print("\n請選擇模式：")
    print("1. 處理本地音訊檔案 (m4a)")
    print("2. 處理 YouTube 影片")
    
    choice = input("請輸入選項 (1/2/)： ")
    
    print("\n請選擇處理方式：")
    print("1. 完整處理（不抽樣）")
    print("2. 抽樣處理（較快但可能遺漏內容）")
    
    process_choice = input("請輸入選項 (1/2)：")
    use_sampling = process_choice == "2"

    try:    
        if choice == "1":
            audio_path = input("請輸入 m4a 檔案路徑：")
            process_local_audio(audio_path, use_sampling)
        elif choice == "2":
            process_youtube_video(use_sampling)
        else:
            print("❌ 無效的選項")
    except Exception as e:
        print(f"❌ 處理過程中發生錯誤：{e}")
        return
        
    print("轉至下一階段...")

if __name__ == "__main__":
    core()
