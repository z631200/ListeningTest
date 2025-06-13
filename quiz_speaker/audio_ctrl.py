from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os
import pygame
import threading
import time

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "output_file")
input_file_path = os.path.join(OUTPUT_DIR, "ListeningTest.txt") 
speech_file_path = os.path.join(OUTPUT_DIR, "speech.mp3") 
speech_test_file_path = os.path.join(OUTPUT_DIR, "speech_test.mp3")

exit_flag = False
paused = False
playing = False  # ✅ 新增，表示是否正在播放


def audio_maker():
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

    load_audio(speech_test_file_path)
    input("按下 Enter 鍵開始播放音訊...")

    while True:
        t = threading.Thread(target=audio_thread)
        t.start()

        # 等待音訊播放完成
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)         

        replay = input("是否再播放一次測試音檔？(y/n)： ").strip().lower()
        if replay != "y":
            print("關閉音量測試...")
            break


def load_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)

def play_audio():
    global playing
    pygame.mixer.music.play()
    playing = True

def pause_audio():
    global paused
    pygame.mixer.music.pause()
    paused = True

def unpause_audio():
    global paused
    pygame.mixer.music.unpause()
    paused = False

def stop_audio():
    global paused, playing
    pygame.mixer.music.stop()
    paused = False
    playing = False  # ✅ 停止播放，但不設 exit_flag

def audio_thread():
    global playing
    play_audio()
    while playing:
        if not pygame.mixer.music.get_busy() and not paused:
            break
        time.sleep(0.5)
    playing = False
    # print("播放完畢。")


def handle_user_commands():
    global exit_flag
    try:
        while not exit_flag:
            if not pygame.mixer.music.get_busy() and not paused:
                print("播放完畢。")
                exit_flag = True
                break

            command = input("輸入指令 (p: 暫停, r: 繼續, s: 停止, q: 離開程式)： ").strip().lower()

            if command == "p":
                pause_audio()
            elif command == "r":
                unpause_audio()
            elif command == "s":
                stop_audio()
                exit_flag = True  # ✅ 讓外部也能知道播放結束
                print("播放已停止。")
                break
            elif command == "q":
                stop_audio()
                exit_flag = True
                print("離開程式。")
                break
    except KeyboardInterrupt:
        print("\n已偵測到 Ctrl+C，正在中止...")
        stop_audio()
        exit_flag = True



def core(full_execution=False):
    global exit_flag

    if full_execution:
        audio_maker()
    else:
        make_audio = input("製作題目語音檔？(y/n)： ").lower()
        if make_audio == "y":
            audio_maker()

    use_command = input("是否啟用指令控制？(y/n)： ").lower()
    if use_command != "y":
        print("將自動播放音訊...")
    else:
        print("進入指令控制模式，輸入指令後將開始播放。")
        print("p: 暫停, r: 繼續, s: 停止, q: 離開")

    load_audio(speech_file_path)
    input("按下 Enter 鍵開始播放音訊...")
    t = threading.Thread(target=audio_thread)
    t.start()

    if use_command == "y":
        handle_user_commands()
    else:
        while not exit_flag:
            if not playing:
                break
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        core()
    except KeyboardInterrupt:
        print("\n已偵測到 Ctrl+C，程式結束。")
        stop_audio()
