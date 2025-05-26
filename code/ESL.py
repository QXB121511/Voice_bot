import ESL
import time
from datetime import datetime
 
def connect_to_esl(host, port, password):
    """Connect to the FreeSWITCH ESL server."""
    con = ESL.ESLconnection(host, port, password)
    if con.connected():
        print("Connected to FreeSWITCH ESL")
        return con
    else:
        raise ConnectionError("Could not connect to FreeSWITCH ESL")
 
def originate_call(con, caller, callee,index, context="default", timeout=300):
    """Originate a single call."""
    originate_str = f"{{absolute_codec_string=PCMA,origination_caller_id_number={caller}}}sofia/external/{caller}@192.168.233.52:5080 &bridge({{absolute_codec_string=PCMA,origination_caller_id_number={callee}}}sofia/external/{callee}@192.168.233.6:5080)"
    command = f"bgapi originate {originate_str}"
    print(f"Sending originate command: {command}")
    response = con.bgapi(command)
 
    #con.events("plain", "all")
    #try:
    ## 循环监听事件
    #    while True:
    #        event = con.recvEvent()
    #        if event:
    #            # 获取当前时间
    #            now = datetime.now()
#
    #            # 格式化时间，具体到秒
    #            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
#
    #            # 打印接收到的事件信息
    #            print(f"事件名称: {event.getHeader('Event-Name')}   {current_time}")
    #        
    #            # 检测挂断事件
    #            if event.getHeader("Event-Name") == "CHANNEL_HANGUP_COMPLETE":
    #                print("检测到挂断事件，退出循环")
    #                break
    #except KeyboardInterrupt:
    #    print("监听被手动中止")
    
 
def batch_originate_calls(con, caller,called,nums=1, context="default", timeout=30, call_interval_ms=1000):
    """Batch originate multiple calls with a frequency limit in milliseconds."""
    for i in range(0,nums):
        str=f"{i:03}"
        try:
            while True:
                response = con.api("show", "calls count")
                rList = response.getBody().split(" ")
 
                if len(rList)==2:
                    print (f"当前通话数：{rList[0]}")
                    
                    if int(rList[0])<601:
                        break
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)
            originate_call(con, caller+str, called+str,i, context, timeout)
            time.sleep(call_interval_ms/1000.0)  # Wait for the specified interval (ms) before the next call
        except Exception as e:
            print(f"Failed to originate call from {caller} to {called}: {e}")
        
 
def main():
    # FreeSWITCH ESL server configuration
    host = "192.168.109.91"  # Change to your FreeSWITCH ESL host
    port = 15080  # Default FreeSWITCH ESL port
    password = "knowdee"  # Change to your ESL password
 
 
    # Call frequency limit (interval in milliseconds between calls)
    call_interval_ms = 100  # Adjust this value as needed
 
    try:
        # Connect to FreeSWITCH
        con = connect_to_esl(host, port, password)
 
        # Originate calls in batch with frequency limit
        batch_originate_calls(con, "1098","1095",10000, call_interval_ms=call_interval_ms)
 
    except Exception as e:
        print(f"Error: {e}")
 
if __name__ == "__main__":
    main()