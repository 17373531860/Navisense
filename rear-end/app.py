from map.map import map_text
from video_and_image.VL_MAX import vl_max_text
from audio_text_audio.TTS import audio1, audio2

def main():
    print("\n【多模态视频图片文本内容】")
    print(vl_max_text)
    print("【地图文本内容】")
    print(map_text)

    print("\n【音频变量情况】")
    print("audio1（map.wav）:", "已生成" if audio1 else "未生成")
    print("audio2（vl_max.wav）:", "已生成" if audio2 else "未生成")

if __name__ == "__main__":
    main()