let ws;
let count = 0;

function globalfun(){
    console.log("globalfun");
}

function connectWebSocket() {
  ws = new WebSocket("ws://127.0.0.1:10000/");//远程服务器地址

  ws.onopen = () => {
    if (count)
      ws.send("reconnected");
    else
      ws.send("connected");
    count++;
  };

  ws.onmessage = (event) => {
    console.log("收到消息:", event.data);
    try {
      const result = eval(`globalThis.globalfun = function(){${event.data}};globalfun()`);
      ws.send(result?.toString() ?? "undefined");
    } catch (e) {
      ws.send("Error: " + e.toString());
    }
  };

  ws.onclose = () => {
    console.log("连接关闭，3秒后重连...");
    setTimeout(connectWebSocket, 3000); // 自动重连
  };

  ws.onerror = (err) => {
    console.error("连接错误:", err);
    ws.close(); // 确保错误时断开，触发重连逻辑
  };
}
connectWebSocket();