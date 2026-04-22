#!/usr/bin/env python3
"""
Video transcription script using faster-whisper
Extracts audio from video and transcribes it to Chinese text
"""
import sys
import os
from faster_whisper import WhisperModel

def transcribe_video(video_path, output_path=None):
    """Transcribe video file using faster-whisper"""
    
    if not os.path.exists(video_path):
        print(f"错误：视频文件不存在: {video_path}")
        return False
    
    print(f"开始转录视频: {video_path}")
    print("加载模型...")
    
    # 使用较小的模型以提高速度，支持中文
    model_size = "base"  # 可选: tiny, base, small, medium, large
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    print("开始转录...")
    
    # 转录视频
    segments, info = model.transcribe(
        video_path,
        language="zh",  # 中文
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    print(f"检测到语言: {info.language} (概率: {info.language_probability:.2f})")
    print("转录结果:")
    print("=" * 80)
    
    # 收集所有文本
    full_text = []
    for segment in segments:
        start_time = segment.start
        end_time = segment.end
        text = segment.text.strip()
        timestamp = f"[{start_time:.1f}s - {end_time:.1f}s]"
        full_text.append(f"{timestamp} {text}")
        print(f"{timestamp} {text}")
    
    print("=" * 80)
    print(f"转录完成！共 {len(full_text)} 个片段")
    
    # 保存到文件
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(full_text))
        print(f"已保存到: {output_path}")
    
    return True

if __name__ == "__main__":
    video_path = "/root/.openclaw/workspace/assets/videos/ai_agent_learning.mp4"
    output_path = "/root/.openclaw/workspace/ai_agent_learning_transcript.txt"
    
    transcribe_video(video_path, output_path)
