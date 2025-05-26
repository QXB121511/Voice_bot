
#encoding=utf-8
import json
import tempfile
import requests
import xml.etree.ElementTree as ET
import freeswitch as fs
from freeswitch import *

import ESL
# `UNI_ENGINE`: unimrcp engine
# In Python, `+` is optional for quoted string concatenation, ^_^
UNI_ENGINE = 'detect:unimrcp {start-input-timers=false,' \
        'no-input-timeout=5000,recognition-timeout=5000}'
# this will be ignored by baidu ASR, and `chat-empty` is also available
UNI_GRAMMAR = 'builtin:grammar/boolean?language=en-US;y=1;n=2'

def asr2text(result):
    """fetch recognized text from asr result (xml)"""
    root = ET.fromstring(result)
    node = root.find('.//input[@mode="speech"]')
    text = None
    if node is not None and node.text:
        # node.text is unicode
        text = node.text.encode('utf-8')
    return text

def handler1(session, args):
    call_addr='user/1018'
    session.execute("bridge", call_addr)

def handler(session, args):
    fs.consoleLog('info', '>>> start chatbot service')
    #uuid = "ggg"
    #console_log("1", "... test from my python program\n")
    #session = PySession(uuid)
    session.answer()

    # first 请求proxy-第一句应该返回什么内容，
    answer_sound = Synthesizer()('你好啊，baby。')

    while session.ready():
        # here, we play anser sound and detect user input in a loop
        session.execute('play_and_detect_speech',
                answer_sound + UNI_ENGINE + UNI_GRAMMAR)
        asr_result =  session.getVariable('detect_speech_result')
        if asr_result is None:
            # if result is None, it means session closed or timeout
            fs.consoleLog('CRIT', '>>> ASR NONE')
            break
        try:
            text = asr2text(asr_result)
        except Exception as e:
            fs.consoleLog('CRIT', '>>> ASR result parse failed \n%s' % e)
            continue
        fs.consoleLog('CRIT', '>>> ASR result is %s' % text)
        # len will get correct length with unicode
        if text is None or len(unicode(text, encoding='utf-8')) < 2:
            fs.consoleLog('CRIT', '>>> ASR result TOO SHORT')
            # answer_sound = sound_query('inaudible')
            answer_sound = Synthesizer()('不好意思，我没有听清您的话，请再说一次。')
            continue
        # chat with robot
        # text = Robot()(text)
        fs.consoleLog('CRIT', 'Robot result is %s' % text)
        if not text:
            text = '不好意思，我刚才迷失在人生的道路上了。请问您还需要什么帮助？'
        # speech synthesis
        answer_sound = Synthesizer()(text)
    
    # session close
    fs.msleep(800)
    session.hangup(1)
    # session.set_tts_params("unimrcp", "xiaofang")
    # session.speak("你好啊，我爱你，中国，哎你你，爱你�")
    #session.playFile("/path/to/your.mp3", "")
    #session.speak("Please enter telephone number with area code and press pound sign. ")
    #input = session.getDigits("", 11, "*#", "#", 10000)
    # session.hangup(1)



class Synthesizer:

    def __init__(self):
        self.audiofile = tempfile.NamedTemporaryFile(prefix='session_', suffix='.wav')

    def __call__(self, text):
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        audio = requests.post("http://127.0.0.1:8001/tts_text", files=dict(text=(None, text))).content
        import uuid
        name = str(uuid.uuid1())
        filename = "/tmp/" + name
        with open(filename, "wb") as file:
            file.write(audio.decode())
        return filename
    