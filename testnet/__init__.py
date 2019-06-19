import time

from solc import compile_source

from web3 import Web3, HTTPProvider
# we will be connecting to the rinkby testnet. the rinkby test net is a PoA network
# whereas the mainnet is a PoW network. to understand the full difference between the two,
# read https://github.com/poanetwork/wiki/wiki/What-is-POA
# because of these differences, we want to add a PoA middleware. web3py's default is PoW
from web3.middleware import geth_poa_middleware


VOTING_CANDIDATES = [b'Rama', b'Nick', b'Jose']

# add your https://infura.io/ API key below
INFURA_API_KEY = 'dde6949be2d84bcbae0ad52953ffa8fc'
INFURA_URL = f'https://rinkeby.infura.io/v3/{INFURA_API_KEY}'
# add your public and private keys below
PUBLIC_KEY = '0xc9864093f3dcb89772fd57dee5233a2196a5c7bd'
PRIVATE_KEY = '5aaeaba436a40cd27b7a794cfe75e4a27820d851c2f82fb46cb256c7e8452d6e'

http_provider = HTTPProvider(INFURA_URL)
web3_provider = Web3(http_provider)

# add the PoA middleware we imported above
# we set layer to zero because we want the PoA middleware to be as "first as possible
web3_provider.middleware_stack.inject(geth_poa_middleware, layer=0)
eth_provider = web3_provider.eth

with open('voting.sol') as file:
    source_code = file.readlines()

compiled_code = compile_source(''.join(source_code))
contract_name = 'Voting'

contract_bytecode = compiled_code[f'<stdin>:{contract_name}']['bin']
contract_abi = compiled_code[f'<stdin>:{contract_name}']['abi']

contract_factory = eth_provider.contract(abi=contract_abi, bytecode=contract_bytecode)
contract_constructor = contract_factory.constructor(VOTING_CANDIDATES)

# toChecksumAddress formats our wallet address string for easy use
wallet_address = web3_provider.toChecksumAddress(PUBLIC_KEY)


def prepare_and_send_transaction(unsigned_transaction):
    # the transaction is coming from our wallet
    unsigned_transaction['from'] = wallet_address

    # every transaction we send need's a nonce
    # our wallet tries to send transactions out in a queue. the earlier the nonce, the sooner the
    # transaction goes out. this helps our wallet and the network respect transactions we might
    # already have floating around on the network waiting to be confirmed
    nonce = eth_provider.getTransactionCount(wallet_address)
    unsigned_transaction['nonce'] = nonce

    # we get a quote for the gas price from the node we're connected to
    gas_price = eth_provider.gasPrice
    # we overwrite the pre-existing gas_price. the gas price initially quoted by the contract is
    # very high. the price quoted by our eth connection is lower in cost and still functional
    unsigned_transaction['gasPrice'] = gas_price

    # TODO: why is this the gas?
    unsigned_transaction['gas'] = 2000000

    # use our private key to sign the transaction. this means it came from our wallet
    signed_transaction = eth_provider.account.signTransaction(unsigned_transaction, PRIVATE_KEY)
    # send the signed transaction to the test net
    transaction_hash = eth_provider.sendRawTransaction(signed_transaction.rawTransaction)

    # ping the testnet every 2 seconds until our transaction is accepted
    transaction_receipt = None
    while transaction_receipt is None:
        transaction_receipt = eth_provider.getTransactionReceipt(transaction_hash)
        if transaction_receipt:
            print('transaction receipt returned')
            break
        # if we didn't get a receipt back, wait for the transaction to be accepted
        time.sleep(2)
        print('waiting for transaction')

    return transaction_receipt
