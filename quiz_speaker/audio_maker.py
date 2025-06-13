from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_file")
input_file_path = os.path.join(OUTPUT_DIR, "ListeningTest.txt") 
speech_file_path = os.path.join(OUTPUT_DIR, "speech.mp3") 
speech_test_file_path = os.path.join(OUTPUT_DIR, "speech_test.mp3")


def make_audio():
    print(CURRENT_DIR)
    print(BASE_DIR)
    print(OUTPUT_DIR)
    print(input_file_path)
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 過濾掉 Answer 行
        filtered_lines = [line.strip() for line in lines if not line.strip().startswith("Answer:")]
        
        # 在每個 Question 開頭之間插入 '...' 作為停頓提示
        modified_lines = []
        for line in filtered_lines:
            # if line.startswith("Question") and modified_lines:
            #     modified_lines.append("<=====>")
            #     # modified_lines.append("...")
            modified_lines.append(line)

        input_text = "\n".join(modified_lines).strip()
        # print(input_text)

    except FileNotFoundError:
        print("找不到 ListeningTest.txt 檔案。")
        return
    except Exception as e:
        print(f"讀取 ListeningTest.txt 發生錯誤: {str(e)}")
        return

    print("正在產生題目語音檔...")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=input_text,
        speed=0.9,
        instructions="Please speak clearly and articulate every word. " \
                        "Maintain a steady pace and proper enunciation for better understanding.",
    ) as response:
        response.stream_to_file(speech_file_path)
        print("題目語音檔已完成...")
        print(f"音訊已儲存至 {speech_file_path}")

def audio_test():
    print("\n正在產生音量測試語音檔...")
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input="Please adjust the volume. This is a test audio file.",
    ) as response:
        response.stream_to_file(speech_test_file_path)
        print("測試語音檔已完成...")
        print(f"音訊已儲存至 {speech_test_file_path}")


