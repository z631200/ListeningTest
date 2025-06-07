import os
import subprocess
from pydub import AudioSegment
from config import SEGMENT_LEN_MS

# 1️⃣ 設定工具路徑
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOL_DIR = os.path.join(BASE_DIR, "tool")
FFMPEG_PATH = os.path.join(TOOL_DIR, "ffmpeg.exe")

# 2️⃣ 驗證工具是否存在
if not os.path.isfile(FFMPEG_PATH):
    raise FileNotFoundError(f"❌ 找不到 ffmpeg 執行檔: {FFMPEG_PATH}")

# 3️⃣ 將音訊轉換成 WAV 格式
def convert_to_wav(input_path: str) -> str:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"❌ 找不到音訊檔案: {input_path}")

    # 取得檔案名稱（不含副檔名）
    file_name = os.path.splitext(input_path)[0]
    output_path = f"{file_name}.wav"
    
    if os.path.exists(output_path):
        os.remove(output_path)

    cmd = [FFMPEG_PATH, "-y", "-i", input_path, output_path]
    print("📤 執行 ffmpeg 轉檔：", " ".join(cmd))

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ ffmpeg 成功轉檔為 WAV")
    except subprocess.CalledProcessError as e:
        print("❌ ffmpeg 執行錯誤：")
        print(e.stderr.decode())
        raise RuntimeError("ffmpeg 轉檔失敗")

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"❌ ffmpeg 雖然執行，但找不到輸出的 WAV：{output_path}")

    return output_path

# 4️⃣ 將音訊切成片段
def split_audio(file_path: str):
    print(f"🎧 開始切割音訊：{file_path}")
    wav_path = convert_to_wav(file_path)

    try:
        audio = AudioSegment.from_wav(wav_path)
    except Exception as e:
        print(f"❌ 無法載入 WAV 音訊：{e}")
        raise RuntimeError("載入音訊失敗")

    duration_ms = len(audio)
    segments = []

    for i in range(0, duration_ms, SEGMENT_LEN_MS):
        segments.append({
            "audio": audio[i:i + SEGMENT_LEN_MS],
            "start_ms": i,
            "end_ms": min(i + SEGMENT_LEN_MS, duration_ms)
        })

    print(f"✅ 切割完成，共 {len(segments)} 段，總長 {duration_ms / 1000:.2f} 秒")
    return segments, duration_ms
