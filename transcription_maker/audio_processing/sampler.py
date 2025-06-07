import os
import random
import subprocess
from pydub import AudioSegment
from config import SAMPLE_PORTION, SAMPLED_AUDIO_FILE, SEGMENT_LEN_MS

# 設定 ffmpeg 路徑
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOL_DIR = os.path.join(BASE_DIR, "tool")
FFMPEG_PATH = os.path.join(TOOL_DIR, "ffmpeg.exe")

OUTPUT_DIR = os.path.join(BASE_DIR, "output_file")
os.makedirs(OUTPUT_DIR, exist_ok=True)  # 若資料夾不存在則建立
SAMPLED_AUDIO_FILE = os.path.join(OUTPUT_DIR, SAMPLED_AUDIO_FILE)

def process_full_audio(segments, duration_ms):
    """處理完整音訊（不抽樣）"""
    combined = AudioSegment.empty()
    segment_offset_map = []
    current_ms = 0

    for seg in segments:
        seg_len = len(seg["audio"])
        segment_offset_map.append({
            "new_start_ms": current_ms,
            "new_end_ms": current_ms + seg_len,
            "original_start_ms": seg["start_ms"],
            "original_end_ms": seg["end_ms"]
        })
        combined += seg["audio"]
        current_ms += seg_len

    # 匯出為中繼 wav
    wav_path = SAMPLED_AUDIO_FILE.replace(".mp3", ".wav")
    print(f"🎧 匯出完整 WAV：{wav_path}")
    combined.export(wav_path, format="wav")

    # 用 ffmpeg 轉成 mp3
    print(f"🎧 使用 ffmpeg 轉為 MP3：{SAMPLED_AUDIO_FILE}")
    try:
        subprocess.run([
            FFMPEG_PATH, "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", SAMPLED_AUDIO_FILE
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ 完整音訊匯出完成：{SAMPLED_AUDIO_FILE}")
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 轉 mp3 錯誤：")
        print(e.stderr.decode())
        raise RuntimeError("MP3 匯出失敗")
    return SAMPLED_AUDIO_FILE, segment_offset_map

def sample_segments(segments, duration_ms):
    """抽樣處理音訊"""
    target_duration = int(duration_ms * SAMPLE_PORTION)
    per_part = target_duration // 3
    total = len(segments)
    third = total // 3

    parts = {
        "前段": segments[:third],
        "中段": segments[third:2 * third],
        "後段": segments[2 * third:]
    }

    selected_segments = []
    for label, part in parts.items():
        selected_segments += random_sample(part, label, per_part)

    combined = AudioSegment.empty()
    segment_offset_map = []
    current_ms = 0

    for seg in selected_segments:
        seg_len = len(seg["audio"])
        segment_offset_map.append({
            "new_start_ms": current_ms,
            "new_end_ms": current_ms + seg_len,
            "original_start_ms": seg["start_ms"],
            "original_end_ms": seg["end_ms"]
        })
        combined += seg["audio"]
        current_ms += seg_len

    # 匯出為中繼 wav
    wav_path = SAMPLED_AUDIO_FILE.replace(".mp3", ".wav")
    print(f"🎧 匯出中繼 WAV：{wav_path}")
    combined.export(wav_path, format="wav")

    # 用 ffmpeg 轉成 mp3
    print(f"🎧 使用 ffmpeg 轉為 MP3：{SAMPLED_AUDIO_FILE}")
    try:
        subprocess.run([
            FFMPEG_PATH, "-y", "-i", wav_path,
            "-codec:a", "libmp3lame", SAMPLED_AUDIO_FILE
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ 抽樣音訊匯出完成：{SAMPLED_AUDIO_FILE}")
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 轉 mp3 錯誤：")
        print(e.stderr.decode())
        raise RuntimeError("MP3 匯出失敗")
    return SAMPLED_AUDIO_FILE, segment_offset_map

def random_sample(partition, label, duration_ms):
    num_chunks = duration_ms // SEGMENT_LEN_MS
    indices = list(range(len(partition)))
    random.shuffle(indices)

    selected = []
    current = 0
    for i in indices:
        if current >= duration_ms:
            break
        seg = partition[i]
        selected.append(seg)
        current += len(seg["audio"])

    print(f"從【{label}】隨機抽取 {len(selected)} 段，共 {current / 1000:.1f}s")
    return selected
