# Your_First_Decentralized_Application_Python

This code borrows HEAVILY from https://github.com/llSourcell/Your_First_Decentralized_Application

Please head over there and toss a star on the repository. llSourcell created a wonderful tutorial to learn from.

## Overview

The functionality of this repo is nearly identical to Your_First_Decentralized_Application but the backend implementation is done in python!

## Setup

1. Create a virtual environment
1. Install dependencies with `pip install -r requirements.txt`
1. Install the `testrpc` command line tool with `npm install -g ethereumjs-testrpc`. I have found the JavaScript tooling for testrpc to be fantastic and easy to use

## Usage

Open up two tabs. In the first tab run `testrpc`. This will start a block chain locally that we can play with. In the second tab activate your virtual environment and run `python main.py`.

After `main.py` finishes running, you'll notice something similar to:
```
  Transaction: 0x0a0a2e25665abb6facf1b66bc561740a488704e06125d7fe60ddea94a04a493b
  Contract created: 0x4c34619c8a98cb91cd3d5da46ef89bdaf5ed50e6
  Gas usage: 352112
  Block Number: 1
  Block Time: Thu Oct 26 2017 16:06:40 GMT+0100 (BST)
```
in the first terminal tab. This is the contract getting deployed to your local chain.

The value we want is the address code after `Contract created: `. Copy the address value and go into `index.js`. Replace the address value of `const contractAddress` with the value you copied.

Lastly open `index.html` in your browser of choice. The web application will connect to testrpc and use it as the backend.

Congrats! You setup your first decentralized application with python!