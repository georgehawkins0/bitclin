import asyncio
import websockets
import json
from datetime import datetime
import argparse
import requests

async def utxfeed(mode,bitcoin_address,lower_limit):
    SATOSHI = 100_000_000 # see comment on line 35
    async with websockets.connect("wss://ws.blockchain.info/inv") as client:
        cmd = '{"op":"unconfirmed_sub"}' # this is the command to start the websocket for unconfirmed transaction feed
        await client.send(cmd)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if mode == "utx_feed":
            if lower_limit != 0:
                print(f"Bitcoin unconfirmed transaction feed (above {lower_limit} BTC) started @ {dt_string}")
            else:
                print(f"Bitcoin unconfirmed transaction feed started @ {dt_string}")
            print("\n")
            print("Hash                                                                  Amount (BTC)    Time")

        elif mode == "watch_address":
            print(f"Started watching address {bitcoin_address} @ {dt_string}")
            print("\n")
        
        while True: # ---v  this part is the constant loop for receiving and printing the feed  v---
            response = await client.recv()
            response = json.loads(response)
            if response["op"] == "utx" and mode == "utx_feed":
                transacted = 0
                for i in response["x"]["out"]:
                    transacted += i["value"]
                bitcoins = transacted / SATOSHI # one bitcoin is 100_000_000 satoshis. The data from the blockchain (and thus the blockchain.com api) is in sats.
                if bitcoins >= lower_limit:
                    time = datetime.utcfromtimestamp(response["x"]["time"]).strftime('%H:%M:%S')
                    tx_hash = response["x"]["hash"]
                    print_distance = (16-len(str(bitcoins)))*" " # calculates how much whitespace should be between the amount(btc) and the time to make a neat "table"
                    print(f"{tx_hash}      {bitcoins}{print_distance}{time}")
        
            elif response["op"] == "utx" and mode == "watch_address":
                nature = None
                for input in response["x"]["inputs"]:
                    if bitcoin_address == input["prev_out"]["addr"]:
                        nature = "received"
                for output in response["x"]["out"]:
                    if bitcoin_address == output["addr"]:
                        nature = "sent"
                total = 0
                for output in response["x"]["out"]:
                    total += output["value"]
                total_btc = total/SATOSHI
                if nature:
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"Address has {nature} a transaction of {total_btc} BTC!                              {dt_string}")
                    hash = response["x"]["hash"]
                    print(f"TX Hash: {hash}")
                    print("\n")

async def blockfeed():
    SATOSHI = 100_000_000
    async with websockets.connect("wss://ws.blockchain.info/inv") as client:        
        cmd = '{"op":"blocks_sub"}' # this is the command to start the websocket for block feed
        await client.send(cmd)
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(f"Bitcoin block feed started @ {dt_string}")
        print("\n")
        print("Hash                                                                  Block Height      Total transaction volume (BTC)      Number of transactions      Fee             Time")
        while True: # ---v  this part is the constant loop for receiving and printing the feed  v---
            response = await client.recv()
            response = json.loads(response)
            if response["op"] == "block":
                block_hash = response["x"]["hash"]
                height = response["x"]["height"]
                response = get_block_info(block_hash) # because when the client recives it from the websocket, a lot of the information is missing.
                n_tx = response["n_tx"]
                total_btc_sent = 0
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                fee = response["fee"]/SATOSHI
                for tx in response["tx"]:
                    for output in tx["out"]:
                        total_btc_sent += output["value"]/SATOSHI
                btc_sent_print_distance = (18-len(str(height)))*" "
                n_tx_print_distance = (36-len(str(total_btc_sent)))*" "
                fee_print_distance = (28-len(str(n_tx)))*" "
                dt_string_print_distance = (10-len(str(n_tx)))*" "
                print(f"{block_hash}      {height}{btc_sent_print_distance}{total_btc_sent}{n_tx_print_distance}{n_tx}{fee_print_distance}{fee}{dt_string_print_distance}{dt_string}")
            
def get_block_info(block_hash):
    r = requests.get(f"https://blockchain.info/rawblock/{block_hash}")
    response_json = r.json()
    return response_json

def get_hashrate():
    r = requests.get(f"https://blockchain.info/q/hashrate")
    response_text = r.text
    return response_text

def get_day_tx_count():
    r = requests.get(f"https://blockchain.info/q/24hrtransactioncount")
    response_text = r.text
    return response_text

def get_address_info(bitcoin_address):
    r = requests.get(f"https://blockchain.info/rawaddr/{bitcoin_address}")
    response_json = r.json()
    if "error" not in response_json:
        return response_json
    return None

parser = argparse.ArgumentParser(description="A cli interface to show current bitcoin network statistics.")
parser.add_argument('-uf', '--utxfeed', help='Print live Unconfirmed Transaction Feed (Mempool) to console.', action='store_true')
parser.add_argument('-bf', '--blockfeed', help='Print live block feed to console.', action='store_true')
parser.add_argument('-w', '--watch', help='Watch a bitcoin address for sent or received transactions.', action='store_true')
parser.add_argument('-b', '--balance', help='Returns the balance of the address specified.', action='store_true')
parser.add_argument('-a', '--address', type=str, help="The bitcoin address.", default=None)
parser.add_argument('-ha', '--hashrate', help='Returns the network\'s current total hashrate', action='store_true')
parser.add_argument('-t', '--tx_count', help='Returns the amount of bitcoin transactions sent in the past 24 hours.', action='store_true')
parser.add_argument('-l', '--tx_lower_limit', help='For use with utx feed. A lower limit. Only transactions with a bitcoin transaction value equal or higher to the limit will be printed to the command line.',type=float,default=0)

if __name__ == "__main__":
    SATOSHI = 100_000_000
    args = parser.parse_args()
    if args.utxfeed and args.blockfeed:
        print("Cant run both utx feed and block feed in same CMD window.")
        
    elif args.utxfeed:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(utxfeed("utx_feed",None,args.tx_lower_limit))

    elif args.blockfeed:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(blockfeed())

    elif args.watch and args.address:
        address_info = get_address_info(args.address)   
        if not address_info:
            print("Invalid bitcoin address")
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(utxfeed("watch_address",args.address,None))

    elif args.hashrate:
        hashrate = get_hashrate()
        hashrate = int(hashrate)/1_000_000_000 # this is the Terrahashes per second (in million)
        print(f"The bitcoin network currently has an estimated total hashrate of {round(hashrate,3)}m TH/s")

    elif args.tx_count:
        count = get_day_tx_count()
        print(f"In the past 24 hours, the bitcoin network has sent {count} transactions.")

    elif args.balance and args.address:
        address_info = get_address_info(args.address)   
        if not address_info:
            print("Invalid bitcoin address")
        else:
            final_balance = address_info["final_balance"]
            print (f"{final_balance/SATOSHI} BTC") 