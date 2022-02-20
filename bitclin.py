import asyncio
import websockets
import json
from datetime import datetime
import argparse

async def main(lower_limit):
    async with websockets.connect("wss://ws.blockchain.info/inv") as client:
        cmd = '{"op":"unconfirmed_sub"}' # this is the command to start the websocket feed
        await client.send(cmd)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if lower_limit != 0:
            print(f"Bitcoin unconfirmed transaction feed (above {lower_limit} BTC) started @ {dt_string}")
        else:
            print(f"Bitcoin unconfirmed transaction feed started @ {dt_string}")
        print("\n")
        print("Hash                                                                  Amount (BTC)    Time")
        while True: # ---v  this part is the constant loop for receiving and printing the transactions  v---
            response = await client.recv()
            response = json.loads(response)
            if response["op"] == "utx":
                SATOSHI = 100_000_000 # see comment on line 24
                transacted = 0
                for i in response["x"]["out"]:
                    transacted += i["value"]

                bitcoins = transacted / SATOSHI # one bitcoin is 100_000_000 satoshis. The data from the blockchain (and thus the blockchain.com api) is in sats.
                if bitcoins >= lower_limit:
                    time = datetime.utcfromtimestamp(response["x"]["time"]).strftime('%H:%M:%S')
                    tx_hash = response["x"]["hash"]
                    print_distance = (16-len(str(bitcoins)))*" " # calculates how much whitespace should be between the amount(btc) and the time to make a neat "table"
                    print(f"{tx_hash}      {bitcoins}{print_distance}{time}")
                
parser = argparse.ArgumentParser(description="A live feed of all unconfirmed bitcoin transactions that are sent to the bitcoin network.")
parser.add_argument('-f', '--feed', help='Print live feed to console.', action='store_true')
parser.add_argument('-l', '--lower_limit', help='A lower limit. Only transactions with a bitcoin transaction value equal or higher to the limit will be printed to the command line.',type=float,default=0)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.feed:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(args.lower_limit))