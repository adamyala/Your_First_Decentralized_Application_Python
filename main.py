# web3 is needed to interact with eth contracts
import web3
# solc is needed to compile our Solidity code
from solc import compile_source

# load our Solidity code into an object
with open('voting.sol') as file:
    source_code = file.readlines()

# compile the contract
compiled_code = compile_source(''.join(source_code))

# open a connection to the testrpc
provider = web3.Web3(web3.HTTPProvider('http://localhost:8545'))

contract_bytecode = compiled_code['<stdin>:Voting']['bin']
# create a contract factory. we'll use this to deploy any number of 
# instances of the contract to the chain
token_contract_factory = web3.contract.construct_contract_factory(
    web3=provider,
    abi=compiled_code['<stdin>:Voting']['abi'],
    code=contract_bytecode,
    code_runtime=compiled_code['<stdin>:Voting']['bin-runtime'],
    source=source_code,
)
token_contract_factory.bytecode = contract_bytecode

# use our factory to create a specific instance of the Voting contract
token_contract = token_contract_factory.factory(provider, 'Voting')
# we'll use one of our default accounts to deploy from
default_account = provider.eth.accounts[0]
# we deploy our contract to the chain and pass in a list of the args needed to 
# initialize the Solidity contract
token_contract.deploy(
    transaction={
        'from': default_account,
    },
    args=[['Rama', 'Nick', 'Jose']],
)
