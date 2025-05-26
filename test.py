import struct  
import time  
import numpy as np  
  
def create_audio_packet(pcm_data, is_tts_playing=False):  
    """  
    创建符合服务器要求的音频数据包  
      
    Args:  
        pcm_data: PCM音频数据 (numpy array 或 bytes)  
        is_tts_playing: TTS播放状态标志  
      
    Returns:  
        bytes: 完整的音频数据包  
    """  
    # 生成当前时间戳（毫秒）  
    timestamp_ms = int(time.time() * 1000) & 0xFFFFFFFF  
      
    # 设置标志位（bit 0 表示TTS播放状态）  
    flags = 1 if is_tts_playing else 0  
      
    # 打包8字节头部（大端字节序）  
    header = struct.pack("!II", timestamp_ms, flags)  
      
    # 如果PCM数据是numpy数组，转换为bytes  
    if isinstance(pcm_data, np.ndarray):  
        pcm_bytes = pcm_data.astype(np.int16).tobytes()  
    else:  
        pcm_bytes = pcm_data  
      
    # 组合头部和音频数据  
    return header + pcm_bytes 


import wave

def wav_to_pcm_bytes(file_path):
    """
    从WAV文件中提取PCM数据并返回字节流

    :param file_path: WAV文件的路径
    :return: PCM数据的字节流（bytes）
    """
    try:
        # 打开WAV文件
        with wave.open(file_path, 'rb') as wav_file:
            # 读取PCM数据
            pcm_data = wav_file.readframes(wav_file.getnframes())
        return pcm_data
    except FileNotFoundError:
        print(f"文件未找到，请检查路径是否正确：{file_path}")
        return None
    except wave.Error as e:
        print(f"读取WAV文件时发生错误：{e}")
        return None
    except Exception as e:
        print(f"发生未知错误：{e}")
        return None

# 示例用法
if __name__ == "__main__":
    wav_file_path = "/data2/qinxb/AUDIO/samples/example.wav"  # 替换为你的WAV文件路径
    pcm_bytes = wav_to_pcm_bytes(wav_file_path)
    if pcm_bytes:
        print(f"PCM数据已成功提取，字节流长度：{len(pcm_bytes)}")
        print(pcm_bytes)
        # 如果需要将PCM字节流保存到文件，可以取消注释以下代码
        # with open("/data2/qinxb/AUDIO/samples/output_pcm.bin", "wb") as output_file:
        #     output_file.write(pcm_bytes)
    else:
        print("未能成功提取PCM数据")