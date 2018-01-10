# we'll need the json module to setup some of our frontend dependencies at the end of the script
import json
# web3 is needed to interact with eth contracts
from web3 import Web3, HTTPProvider
# solc is needed to compile our Solidity code
from solc import compile_source

# load our Solidity code into an object
with open('voting.sol') as file:
    source_code = file.readlines()

# compile the contract
compiled_code = compile_source(''.join(source_code))

# open a connection to the testrpc
http_provider = HTTPProvider('http://localhost:8545')
eth_provider = Web3(http_provider).eth

# contract name so we keep our code DRY
contract_name = 'Voting'

# lets make the code a bit more readable by storing the values in variables
contract_bytecode = compiled_code[f'<stdin>:{contract_name}']['bin']
contract_abi = compiled_code[f'<stdin>:{contract_name}']['abi']
# the contract abi is important. it's a json representation of our smart contract. this
# allows other APIs like JavaScript to understand how to interact with our contract without
# reverse engineering our compiled code

# create a contract factory. we'll use this to deploy any number of 
# instances of the contract to the chain
contract_factory = eth_provider.contract(
    abi=contract_abi,
    bytecode=contract_bytecode,
)

# we'll use one of our default accounts to deploy from. every write to the chain requires a
# payment of ethereum called "gas". if we were running an actual test ethereum node locally,
# then we'd have to go on the test net and get some free ethereum to play with. that is beyond
# the scope of this tutorial so we're using a mini local node that has unlimited ethereum and
# the only chain we're using is our own local one
default_account = eth_provider.accounts[0]

# here we deploy the smart contract
# two things are passed into the deploy function:
#   1. info about how we want to deploy to the chain
#   2. the arguments to pass the smart contract constructor
# the deploy() function returns a transaction hash. this is like the id of the
# transaction that initially put the contract on the chain
transaction_hash = contract_factory.deploy(
    # the bare minimum info we give about the deployment is which ethereum account
    # is paying the gas to put the contract on the chain
    transaction={
        'from': default_account,
    },
    # here was pass in a list of smart contract constructor arguments
    # our contract constructor takes only one argument, a list of candidate names
    args=[
        ['Rama'.encode(), 'Nick'.encode(), 'Jose'.encode()],
    ],
)

# if we want our frontend to use our deployed contract as it's backend, the frontend
# needs to know the address where the contract is located. we use the id of the transaction
# to get the full transaction details, then we get the contract address from there
transaction_receipt = eth_provider.getTransactionReceipt(transaction_hash)
contract_address = transaction_receipt['contractAddress']

# we don't want to be copy and pasting json and hex addresses into our javascript file
# so we will write the abi (remember this is the json representation of our contract) and the
# contract address to .js files
abi_json_string = json.dumps(contract_abi)
abi_js = f'const abi = {abi_json_string};'
with open('abi.js', 'w') as outfile:
    outfile.write(abi_js)

address_js = f'const contractAddress = "{contract_address}";'
with open('address.js', 'w') as outfile:
    outfile.write(address_js)
