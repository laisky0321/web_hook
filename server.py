import asyncio
import threading
import websockets
from queue import Queue

# 线程安全的输入队列
input_queue = Queue()
lock = 0

def input_thread():
    global lock
    while True:
        if lock == 1:
            cmd = input(f"\033[32mcmd: \033[0m")
            input_queue.put(cmd)
            lock = 0
            # print("\033[2K\033[1G", end='') 
            # print(f"\033[32mcmd: {cmd}\033[0m")

async def recv_handler(websocket):
    try:
        async for message in websocket:
            print(f"\033[34mremote: \033[0m{message}")
            global lock
            lock = 1
    except websockets.exceptions.ConnectionClosedOK:
        print("连接正常关闭")
    except Exception as e:
        print(f"连接异常: {e}")

async def send_handler(websocket):
    loop = asyncio.get_event_loop()
    while True:
        # 异步从线程队列中获取输入
        cmd = await loop.run_in_executor(None, input_queue.get)
        await websocket.send(cmd)

async def handler(websocket):
    print(f"客户端连接: {websocket.remote_address}")
    recv_task = asyncio.create_task(recv_handler(websocket))
    send_task = asyncio.create_task(send_handler(websocket))
    done, pending = await asyncio.wait(
        [recv_task, send_task],
        return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 10000)
    print("服务器启动，监听端口10000")
    # 启动输入线程
    threading.Thread(target=input_thread, daemon=True).start()
    await server.wait_closed()

asyncio.run(main())