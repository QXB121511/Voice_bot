import asyncio  
import websockets  
import json  
import struct  
import numpy as np  
import time  
import logging  
  
# 设置日志以便调试  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)  
  
class CompletePipelineTester:  
    def __init__(self, uri="ws://172.70.10.53:8889/ws"):  
        self.uri = uri  
        self.websocket = None  
      
    async def connect(self):  
        """连接到WebSocket服务器"""  
        try:  
            self.websocket = await websockets.connect(self.uri)  
            logger.info(f"✅ 已连接到 {self.uri}")  
        except Exception as e:  
            logger.error(f"❌ 连接失败: {e}")  
            raise 
         
    async def send_text(self, text: str):    
        """发送文本消息"""    
        await self.websocket.send(text)    
        logger.info(f"✅ 发送文本消息: {text}")

    async def send_realistic_audio(self, wav_path: str):
        """极简版WAV文件发送"""
        # 一次性读取整个文件
        with open(wav_path, 'rb') as f:
            raw_data = f.read()[44:]  # 跳过WAV头44字节（假设标准PCM头）

        # 分包参数
        HEADER_SIZE = 8
        FRAME_SIZE = 2048 * 2  # 2048样本 * 2字节
        CHUNK_SIZE = FRAME_SIZE

        # 拆分音频数据为多个数据包
        for i in range(0, len(raw_data), CHUNK_SIZE):
            # 构造消息包
            header = bytearray(HEADER_SIZE)
            
            # 时间戳（简单递增）
            timestamp = i // CHUNK_SIZE * 300  # 假设每个包300ms
            struct.pack_into("!I", header, 0, timestamp)
            
            # 标志位（保持0）
            struct.pack_into("!I", header, 4, 0)
            
            # 当前数据块（自动截断最后不足部分）
            audio_chunk = raw_data[i:i+CHUNK_SIZE]
            
            # 合并包头和音频数据
            packet = header + audio_chunk
            
            # 发送
            await self.websocket.send(packet)

        print(f"已发送 {len(raw_data)//CHUNK_SIZE} 个音频包")

    async def test_complete_pipeline(self):  
        """测试完整的pipeline"""  
        try:  
            # 连接到服务器  
            await self.connect()  
              
            # 等待连接稳定  
            await asyncio.sleep(5)  
              
            # 发送音频数据  
            await self.send_text('{"type" : "tts_start"}')
            await self.send_realistic_audio(wav_path="/data2/qinxb/AUDIO/samples/wanan.wav") 

            await asyncio.sleep(15)  # 给足够时间让所有组件处理  
              
                  
        except Exception as e:  
            logger.error(f"❌ Pipeline测试失败: {e}")  


async def main():  
    logger.info("🚀 开始完整Pipeline测试")  
    tester = CompletePipelineTester()  
    await tester.test_complete_pipeline()  
    async for message in tester.websocket:  
        if isinstance(message, str): 
            data = json.loads(message) 
            print("ws输出", data)
    if tester.websocket:  
        await tester.websocket.close()  

if __name__ == "__main__":  
    asyncio.run(main())