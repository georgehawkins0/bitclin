# bitclin
 
(bit-cli-n) 

A CLI program to show statistics about the bitcoin network. Includes a live feed of all unconfirmed bitcoin transactions sent to the bitcoin network, a live feed of blocks as they are mined, and ability to watch a bitcoin address, to receive notifications about activity.

Here are some usage examples:

1. View live unconfirmed transaction feed showing only transactions with a transaction value of more than 1 BTC:

        $ bitclin.py -u -l 1

2. Watch bitcoin address to recieve notifications about transactions sent or received:

        $ bitclin.py --watch -a 1BitcoinEaterAddressDontSendf59kuE
        
## Table of contents

- [Installation](#installation)
- [Usage](#usage)


## Installation
Clone the github repo
```
$ git clone https://github.com/georgehawkins0/bitclin
```
Change Directory

```
$ cd bitclin
```

## Requirements :


For requirements run following commands:


```
$ python3 -m pip install -r requirements.txt
```

## Usage 
### cmdline options
```
usage: bitclin.py [-h] [-u] [-b] [-w] [-bal] [-a ADDRESS] [-ha] [-t] [-l TX_LOWER_LIMIT]

A cli interface to show current bitcoin network statistics.

optional arguments:
  -h, --help            show this help message and exit
  -u, -utx, --utxfeed   Print live Unconfirmed Transaction Feed (Mempool) to console.
  -b, --blockfeed       Print live block feed to console.
  -w, --watch           Watch a bitcoin address for sent or received transactions.
  -bal, --balance       Returns the balance of the address specified.
  -a ADDRESS, --address ADDRESS
                        The bitcoin address.
  -ha, --hashrate       Returns the network's current total hashrate
  -t, --tx_count        Returns the amount of bitcoin transactions sent in the past 24 hours.
  -l TX_LOWER_LIMIT, --tx_lower_limit TX_LOWER_LIMIT
                        For use with utx feed. A lower limit. Only transactions with a bitcoin transaction value equal or higher to the limit will be printed to the command line.
```







### About
Bitclin uses Blockchain.info API for data.

## To-do
- Currently, watching a bitcoin address uses the websocket provided by blockchain.info to get all unconfirmed transactions, and then checks if that transaction is associated with the given bitcoin address. There is a websocket feed to subscribe to a specified address - this would save considerable resources - but I believe this websocket is down - or at least I could not get it to work. There is little on the internet about this, and I could only find [this](https://stackoverflow.com/questions/70796683/why-no-response-from-blockchain-websocket-api) stack overflower discussion on this particular issue. If anyone can get this websocket to work I would be more than grateful! 