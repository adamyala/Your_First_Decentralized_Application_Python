from flask import Flask, request, render_template

from easysolc import Solc

from web3 import Web3, HTTPProvider

from web3.contract import ConciseContract

solc = Solc()

app = Flask(__name__)

VOTING_CANDIDATES = [b'Rama', b'Nick', b'Jose']

http_provider = HTTPProvider('http://localhost:8545')

eth_provider = Web3(http_provider).eth


default_account = eth_provider.accounts[0]

transaction_details = {
    'from': default_account,
}

compiled_code = solc.compile('voting_v5.sol', output_dir='.')
