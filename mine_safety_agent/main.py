import asyncio
import json
import os
import random
import math
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI(title="智慧矿山大屏后端")


# --- 数据模拟 ---

class DataGenerator:
    """模拟两台设备（主皮带机、采煤机）的传感器数据"""

    def __init__(self):
        self._t = 0.0  # 时间步，用于生成平滑波形

    def _sin_wave(self, base: float, amp: float, period: float) -> float:
        return base + amp * math.sin(2 * math.pi * self._t / period)

    def generate(self) -> dict:
        self._t += 1.0

        # 主皮带机
        belt = {
            "temperature": round(self._sin_wave(65, 20, 60) + random.uniform(-3, 3), 1),
            "current":    round(self._sin_wave(150, 12, 45) + random.uniform(-5, 5), 1),
            "vibration":  round(self._sin_wave(2.5, 1.2, 30) + random.uniform(-0.3, 0.3), 2),
        }

        # 采煤机 状态切换
        r = random.random()
        if r < 0.85:
            status = "运行"
        elif r < 0.95:
            status = "待机"
        else:
            status = "故障"

        shearer = {
            "status":   status,
            "voltage":  round(self._sin_wave(3300, 80, 90) + random.uniform(-30, 30), 1),
        }

        return {
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "belt":      belt,
            "shearer":   shearer,
        }


# --- WebSocket ---

class ConnectionManager:
    def __init__(self):
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.add(ws)

    def disconnect(self, ws: WebSocket):
        self._connections.discard(ws)

    async def broadcast(self, payload: str):
        dead: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.discard(ws)


manager = ConnectionManager()
generator = DataGenerator()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # 保持连接存活，数据由 broadcast_loop 统一推送
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_loop())


async def broadcast_loop():
    """每秒生成数据并广播给所有连接的客户端"""
    while True:
        data = generator.generate()
        await manager.broadcast(json.dumps(data, ensure_ascii=False))
        await asyncio.sleep(1)


# --- 页面 & 健康检查 ---

@app.get("/")
@app.get("/index.html")
async def index():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    return FileResponse(path)


@app.get("/health")
async def health():
    return {"status": "ok", "connections": len(manager._connections)}
