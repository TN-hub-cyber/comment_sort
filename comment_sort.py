import streamlit as st
import re
from datetime import datetime, timedelta

def convert_to_seconds(time_str):
    """
    時間文字列を秒数に変換する
    HH:MM:SS または MM:SS 形式に対応
    """
    parts = time_str.strip().split(':')
    if len(parts) == 2:  # MM:SS形式
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS形式
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

def format_time(seconds):
    """
    秒数をHH:MM:SS形式に変換する
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def extract_timestamps(text):
    """
    テキストからタイムスタンプを含む行を抽出する
    - 重複するタイムスタンプは1つだけ残す
    - 1分以内の間隔のタイムスタンプは最も早い時間のものだけ残す
    """
    lines = text.split('\n')
    timestamp_dict = {}  # 重複を排除するために辞書を使用
    
    # タイムスタンプのパターン
    patterns = [
        r'^(\d{1,2}:\d{2}:\d{2})\s*(.*?)$',  # HH:MM:SS
        r'^(\d{1,2}:\d{2})\s*(.*?)$',         # MM:SS
    ]
    
    for line in lines:
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                time_str = match.group(1)
                content = match.group(2)
                
                # 時間文字列を秒数に変換
                seconds = convert_to_seconds(time_str)
                # 常に0埋めした HH:MM:SS 形式で出力
                formatted_time = format_time(seconds)
                
                # 同じ時間のエントリーがまだない場合のみ追加
                if formatted_time not in timestamp_dict:
                    timestamp_dict[formatted_time] = (seconds, content)
                break
    
    # 辞書からタプルのリストを作成してソート
    timestamp_lines = [(time, content) for time, (seconds, content) in timestamp_dict.items()]
    sorted_lines = sorted(timestamp_lines, key=lambda x: convert_to_seconds(x[0]))
    
    # 1分以内の間隔のタイムスタンプをフィルタリング
    filtered_lines = []
    last_seconds = -60  # 最初のタイムスタンプが必ず追加されるように
    
    for time_str, content in sorted_lines:
        current_seconds = convert_to_seconds(time_str)
        if current_seconds - last_seconds >= 60:  # 1分以上の間隔がある場合
            filtered_lines.append((time_str, content))
            last_seconds = current_seconds
    
    return filtered_lines

def main():
    st.title("YouTube タイムスタンプ ソート")
    st.write("YouTubeのコメントからタイムスタンプを抽出し、時系列順に並び替えます。")
    
    # テキストエリアの入力
    input_text = st.text_area(
        "YouTubeのコメントを貼り付けてください",
        height=300
    )
    
    if st.button("並び替え"):
        if input_text:
            # タイムスタンプの抽出と並び替え
            sorted_timestamps = extract_timestamps(input_text)
            
            if sorted_timestamps:
                st.write("### 並び替え結果")
                result_text = "\n".join([f"{time} {content}" for time, content in sorted_timestamps])
                st.text_area("結果", result_text, height=300)
            else:
                st.warning("タイムスタンプが見つかりませんでした。")
        else:
            st.warning("テキストを入力してください。")

if __name__ == "__main__":
    main()
