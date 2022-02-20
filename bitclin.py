import asyncio
import websockets
import json
from datetime import datetime

async def main():
    async with websockets.connect("wss://ws.blockchain.info/inv") as client:
        cmd = '{"op":"unconfirmed_sub"}' # this is the command to start the websocket feed
        await client.send(cmd)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(f"Bitcoin unconfirmed transaction feed started @ {dt_string}")
        print("\n")
        print("Hash                                                                  Amount (BTC)    Time")
        while True:
            response = await client.recv()
            response = json.loads(response)
            if response["op"] == "utx":
                SATOSHI = 100_000_000 # see comment on line 24
                transacted = 0
                for i in response["x"]["out"]:
                    transacted += i["value"]

                bitcoins = transacted / SATOSHI # one bitcoin is 100_000_000 satoshis. The data from the blockchain (and thus the blockchain.com api) is in sats.
                time = datetime.utcfromtimestamp(response["x"]["time"]).strftime('%H:%M:%S')
                tx_hash = response["x"]["hash"]
                print_distance = (16-len(str(bitcoins)))*" " # calculates how much whitespace should be between the amount(btc) and the time to make a neat "table"
                print(f"{tx_hash}      {bitcoins}{print_distance}{time}")
                

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())