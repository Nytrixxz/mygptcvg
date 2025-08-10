# server.py
# Simple websocket signaling server for small rooms (aiohttp)
# Meant to be deployed on Render or similar (supports websockets).
import os
import json
from aiohttp import web

ROOMS = {}  # room_id -> set of websocket

async def index(request):
    return web.Response(text="Signaling server running\n", content_type="text/plain")

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room = None
    peer_name = None

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except:
                    await ws.send_str(json.dumps({"error":"invalid json"}))
                    continue

                action = data.get("action")
                if action == "join":
                    room = data.get("room")
                    peer_name = data.get("name", "anon")
                    if not room:
                        await ws.send_str(json.dumps({"error":"room required"}))
                        continue
                    ROOMS.setdefault(room, set()).add(ws)
                    # notify others
                    for p in list(ROOMS[room]):
                        if p is not ws:
                            await p.send_str(json.dumps({"action":"peer-joined","name":peer_name}))
                    await ws.send_str(json.dumps({"action":"joined","room":room}))
                elif action == "signal":
                    # forward to all others in room
                    room = data.get("room")
                    payload = data.get("data")
                    from_name = data.get("from")
                    if not room or payload is None:
                        continue
                    for p in list(ROOMS.get(room, [])):
                        if p is not ws:
                            try:
                                await p.send_str(json.dumps({"action":"signal","from":from_name,"data":payload}))
                            except:
                                pass
                elif action == "leave":
                    break
                else:
                    await ws.send_str(json.dumps({"error":"unknown action"}))
            elif msg.type == web.WSMsgType.ERROR:
                print('ws exception', ws.exception())
    finally:
        if room and ws in ROOMS.get(room, set()):
            ROOMS[room].remove(ws)
            # notify remaining peers
            for p in list(ROOMS.get(room, [])):
                try:
                    await p.send_str(json.dumps({"action":"peer-left","name":peer_name}))
                except:
                    pass

    return ws

app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/ws', ws_handler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host='0.0.0.0', port=port)
