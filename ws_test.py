import asyncio  
import websockets  
import wave  
import struct  
import time  
import numpy as np  
from scipy.signal import resample_poly  
import json

class WAVWebSocketTester:  
    def __init__(self, wav_file_path, server_url="ws://172.70.10.53:8889/ws"):  
        self.wav_file_path = wav_file_path  
        self.server_url = server_url  
        self.websocket = None  
          
    async def load_and_resample_wav(self):  
        """加载WAV文件并重采样到48kHz（客户端期望的采样率）"""  
        with wave.open(self.wav_file_path, 'rb') as wav_file:  
            # 获取音频参数  
            sample_rate = wav_file.getframerate()  
            n_channels = wav_file.getnchannels()  
            sample_width = wav_file.getsampwidth()  
            n_frames = wav_file.getnframes()  
              
            print(f"原始音频: {sample_rate}Hz, {n_channels}声道, {sample_width}字节/样本")  
              
            # 读取音频数据  
            audio_data = wav_file.readframes(n_frames)  
              
            # 转换为numpy数组  
            if sample_width == 2:  # 16-bit  
                audio_array = np.frombuffer(audio_data, dtype=np.int16)  
            elif sample_width == 4:  # 32-bit  
                audio_array = np.frombuffer(audio_data, dtype=np.int32)  
                audio_array = (audio_array / 65536).astype(np.int16)  # 转换为16-bit  
            else:  
                raise ValueError(f"不支持的样本宽度: {sample_width}")  
              
            # 如果是立体声，转换为单声道  
            if n_channels == 2:  
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)  
              
            # 重采样到48kHz（如果需要）  
            if sample_rate != 8000:  
                print(f"重采样从 {sample_rate}Hz 到 8000Hz")  
                # 使用float32进行精确重采样  
                audio_float = audio_array.astype(np.float32)  
                resampled = resample_poly(audio_float, 8000, sample_rate)  
                audio_array = np.clip(resampled, -32768, 32767).astype(np.int16)  
              
            return audio_array 
        

    async def load_wav(self):  
        with wave.open(self.wav_file_path, 'rb') as wav_file:  
            # 获取音频参数  
            n_frames = wav_file.getnframes()  
            audio_data = wav_file.readframes(n_frames)  
            audio_array = np.frombuffer(audio_data, dtype=np.int16)   
              
            # 使用float32进行精确重采样  
            audio_float = audio_array.astype(np.float32)  
            resampled = resample_poly(audio_float, 8000, 16000)  
            audio_array = np.clip(resampled, -32768, 32767).astype(np.int16)  
              
            return audio_array 
    
    async def send_text(self, text: str):    
        """发送文本消息"""    
        await self.websocket.send(text)    

    async def send_audio_chunks(self, audio_data, chunk_size=2048):  
        """分块发送音频数据，末尾添加静默"""  
        print(f"开始发送音频数据，总长度: {len(audio_data)} 样本")  
        
        # 发送实际音频数据  
        for i in range(0, len(audio_data), chunk_size):  
            chunk = audio_data[i:i + chunk_size]  
            pcm_bytes = chunk.tobytes()  
 
            await self.websocket.send(pcm_bytes)  
            
            duration = chunk_size / 8000.0  
            await asyncio.sleep(duration)  
        
        # 添加静默期（1-2秒的静默音频）  
        silence_duration = 2.0  # 2秒静默  
        silence_samples = int(8000 * silence_duration)  
        silence_audio = np.zeros(silence_samples, dtype=np.int16)  
        
        print("发送静默音频以触发句子结束检测...")  
        for i in range(0, len(silence_audio), chunk_size):  
            chunk = silence_audio[i:i + chunk_size]  
            pcm_bytes = chunk.tobytes()  
            await self.websocket.send(pcm_bytes)  
            
            duration = chunk_size / 8000.0  
            await asyncio.sleep(duration)
      
    async def handle_messages(self):  
        """处理服务器返回的消息"""  
        try:  
            async for message in self.websocket:  
                if isinstance(message, str): 
                    data = json.loads(message) 
                    print("ws输出", data)
        except websockets.exceptions.ConnectionClosed:  
            print("连接已关闭")  
      
    async def run_test(self):  
        """运行测试"""  
        try:  
            # 加载和处理音频文件  
            # audio_data = await self.load_and_resample_wav()  
            audio_data = await self.load_wav()
              
            # 连接WebSocket  
            print(f"连接到 {self.server_url}")  
            async with websockets.connect(self.server_url) as websocket:  
                self.websocket = websocket  
                print("WebSocket连接成功")  
                  
                # 创建消息处理任务  
                message_task = asyncio.create_task(self.handle_messages())  
                  
                await self.send_text('{"type" : "tts_start"}')

                # 测试一段语音
                # 发送音频数据  
                await self.send_audio_chunks(audio_data)  
                  
                print("音频发送完成，等待响应...")  
                  
                # 等待一段时间接收响应  
                await asyncio.sleep(10)  
                # 测试说第二句话
                await self.send_audio_chunks(audio_data) 
                # 测试第三句间隔很短来做到打断
                await self.send_audio_chunks(audio_data) 

                # 等待一段时间接收响应  
                await asyncio.sleep(20)

                # 取消消息处理任务  
                message_task.cancel()  
                  
        except Exception as e:  
            print(f"测试过程中出错: {e}")  
  
# 使用示例  
async def main():  
    # 替换为你的WAV文件路径  
    wav_file = "/data2/qinxb/AUDIO/samples/example.wav"  # 你的WAV文件路径  

    tester = WAVWebSocketTester(wav_file)  
    await tester.run_test()  
  
if __name__ == "__main__":  
    asyncio.run(main())