# 更改为电话端侧的参数

## 1. 修改 server.py

### 1.1 修改ws.send_json()

在 send_tts_chunks() 函数中，600-609行
result = {
    "type": "streamAudio",
    "data": {
        "audioDataType": "raw",
        "sampleRate": 8000,
        "audioData": base64_chunk # Convert bytes to str
    }
}
await ws.send_json(result)

### 1.2 修改四个task变为process_incoming_data_telephone 1028-1033

tasks = [
    asyncio.create_task(process_incoming_data_telephone(ws, app, audio_chunks, callbacks)), # Pass callbacks
    asyncio.create_task(app.state.AudioInputProcessor.process_chunk_queue(audio_chunks)),
    asyncio.create_task(send_text_messages(ws, message_queue)),
    asyncio.create_task(send_tts_chunks(ws, app, message_queue, callbacks)), # Pass callbacks
]

### 1.3 注释掉send_text_messages中的ws.send


## 2. 修改 upsample_overlap.py

### 2.1 修改采样频率

48000全部改为8000

## 3. audio_in.py

### 3.1 修改采样频率

_RESAMPLE_RATIO = 1

resample_poly(audio_float32, 2, 1)

