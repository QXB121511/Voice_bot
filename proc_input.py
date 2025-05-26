import asyncio  
import websockets  
import wave  
import struct  
import time  
import numpy as np  
from scipy.signal import resample_poly  

chunk_size = 2048

def process_input(ws: websockets):

    msg = await ws.receive()
    # print(msg)
    if "bytes" in msg and msg["bytes"]:
        audio_data = msg["bytes"]

        audio_array = np.frombuffer(audio_data, dtype=np.int16) 
        # 使用float32进行精确重采样
        audio_float = audio_array.astype(np.float32)  
        resampled = resample_poly(audio_float, 48000, 8000)  
        audio_array = np.clip(resampled, -32768, 32767).astype(np.int16)
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]  
            pcm_bytes = chunk.tobytes()  
            timestamp_ms = int(time.time() * 1000) & 0xFFFFFFFF  
            # 标志位（bit 0: TTS播放状态）  
            flags = 0