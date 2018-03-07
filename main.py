# flask is a python web framework. it allows us to send and receive user requests
# with a minimal number of lines of non-web3py code. flask is beyond the scope of
# this tutorial so the flask code won't be commented. that way we can focus on
# how we're working with our smart contract
from flask import Flask, request, render_template
# solc is needed to compile our Solidity code
from solc import compile_source
# web3 is needed to interact with eth contracts
from web3 import Web3, HTTPProvider
# we'll use ConciseContract to interact with our specific instance of the contract
from web3.contract import ConciseContract

# initialize our flask app
app = Flask(__name__)

# the candidates we're allowing people to vote for
# note that each name is being encoded to bytes because our contract 
# type is bytes32[]
VOTING_CANDIDATES = ['Rama'.encode(), 'Nick'.encode(), 'Jose'.encode()]

# open a connection to the testrpc
http_provider = HTTPProvider('http://localhost:8545')
eth_provider = Web3(http_provider).eth

# we'll use one of our default accounts to deploy from. every write to the chain requires a
# payment of ethereum called "gas". if we were running an actual test ethereum node locally,
# then we'd have to go on the test net and get some free ethereum to play with. that is beyond
# the scope of this tutorial so we're using a mini local node that has unlimited ethereum and
# the only chain we're using is our own local one
default_account = eth_provider.accounts[0]
# every time we write to the chain it's considered a "transaction". every time a transaction
# is made we need to send with it at a minimum the info of the account that is paying for the gas
transaction_details = {
    'from': default_account,
}

# if not app.config.get('CONTRACT_ADDRESS'):
# load our Solidity code into an object
with open('voting.sol') as file:
    source_code = file.readlines()

# compile the contract
compiled_code = compile_source(''.join(source_code))

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

# here we deploy the smart contract
# two things are passed into the deploy function:
#   1. info about how we want to deploy to the chain
#   2. the arguments to pass the smart contract constructor
# the deploy() function returns a transaction hash. this is like the id of the
# transaction that initially put the contract on the chain
transaction_hash = contract_factory.deploy(
    # the bare minimum info we give about the deployment is which ethereum account
    # is paying the gas to put the contract on the chain
    transaction=transaction_details,
    # here was pass in a list of smart contract constructor arguments
    # our contract constructor takes only one argument, a list of candidate names
    args=[VOTING_CANDIDATES],
)

# if we want our frontend to use our deployed contract as it's backend, the frontend
# needs to know the address where the contract is located. we use the id of the transaction
# to get the full transaction details, then we get the contract address from there
transaction_receipt = eth_provider.getTransactionReceipt(transaction_hash)
contract_address = transaction_receipt['contractAddress']

contract_instance = eth_provider.contract(
    abi=contract_abi,
    address=contract_address,
    # when a contract instance is converted to python, way call the native solidity
    # functions like: contract_instance.call().someFunctionHere()
    # the .call() notation becomes repetitive so we can pass in ConciseContract as our
    # parent class, allowing us to make calls like: contract_instance.someFunctionHere()
    ContractFactoryClass=ConciseContract,
)


@app.route('/', methods=['GET', 'POST'])
def index():
    alert = ''
    candidate_name = request.form.get('candidate')
    if request.method == 'POST' and candidate_name:
        # if we want to pass a candidate name to our contract then we have to convert it to bytes
        candidate_name_bytes = candidate_name.encode()
        try:
            # the typical behavior of a solidity function is to validate inputs before
            # executing the function. remember that work on the chain is permanent so
            # we really want to be sure we're running it when appropriate.
            #
            # in the case of voteForCandidate, we check to see that the passed in name
            # is actually one of the candidates we specified on deployment. if it's not,
            # the contract will throw a ValueError which we want to catch
            contract_instance.voteForCandidate(candidate_name_bytes, transact=transaction_details)
        except ValueError:
            alert = f'{candidate_name} is not a voting option!'

    # the web3py wrapper will take the bytes32[] type returned by .getCandidateList()
    # and convert it to a list of strings
    candidate_names = contract_instance.getCandidateList()
    # solidity doesn't yet understand how to return dict/mapping/hash like objects
    # so we have to loop through our names and fetch the current vote total for each one.
    candidates = {}
    for candidate_name in candidate_names:
        votes_for_candidate = contract_instance.totalVotesFor(candidate_name)
        # we have to convert the candidate_name back into a string. we get it back as bytes32
        # we also want to strip the tailing \x00 empty bytes if our names were shorter than 32 bytes
        # if we don't strip the bytes then our page will say "Rama\x00\x00\x00\x00\x00\x00\x00\x00"
        candidate_name_string = candidate_name.decode().rstrip('\x00')
        candidates[candidate_name_string] = votes_for_candidate

    return render_template('index.html', candidates=candidates, alert=alert)


if __name__ == '__main__':
    # set debug=True for easy development and experimentation
    # set use_reloader=False. when this is set to True it initializes the flask app twice. usually
    # this isn't a problem, but since we deploy our contract during initialization it ends up getting
    # deployed twice. when use_reloader is set to False it deploys only once but reloading is disabled
    app.run(debug=True, use_reloader=False)
