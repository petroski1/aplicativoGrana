import asyncio
import websockets
import json

TOKEN = 'pat_6f698b4757532db74d2f8f3cb8f530873bfa36c331fc949eeffb8155ee0f1d8c'
APP_IDS = [1089, 16929, 35148, 36544, 19111, 11780, 9999, 36300, 36776, 40163]

async def test(app_id):
    try:
        url = f'wss://ws.derivws.com/websockets/v3?app_id={app_id}'
        async with websockets.connect(url, open_timeout=5) as ws:
            await ws.send(json.dumps({'authorize': TOKEN}))
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            if 'error' in resp:
                print(f'app_id {app_id}: ERRO - {resp["error"]["code"]}')
            else:
                bal = resp['authorize']['balance']
                login = resp['authorize']['loginid']
                print(f'app_id {app_id}: OK! balance={bal} login={login}')
    except Exception as e:
        print(f'app_id {app_id}: FALHA - {e}')

async def main():
    for app_id in APP_IDS:
        await test(app_id)

asyncio.run(main())
