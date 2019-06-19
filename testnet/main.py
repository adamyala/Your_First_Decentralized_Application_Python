from flask import Flask, request, render_template

from testnet import eth_provider, contract_abi, prepare_and_send_transaction


app = Flask(__name__, template_folder='../templates/')

# load the contract address from our file
with open('testnet/contract_address.txt') as file:
    contract_address = file.readline()

# this time we don't need the byte code, just the abi (so we know how to interact with
# the contract) and the contract address (so the network knows where to send our transaction)
contract_instance = eth_provider.contract(abi=contract_abi, address=contract_address)


@app.route('/', methods=['GET', 'POST'])
def index():
    alert = ''
    candidate_name = request.form.get('candidate')
    if request.method == 'POST' and candidate_name:
        candidate_name_bytes = candidate_name.encode()
        try:
            contract_function = contract_instance.functions.voteForCandidate(candidate_name_bytes)
            transaction_details = contract_function.buildTransaction()
            transaction_receipt = prepare_and_send_transaction(transaction_details)
            if not transaction_receipt['status'] == 1:
                alert = f'Vote for {candidate_name} failed! Try again.'

        except ValueError:
            alert = f'{candidate_name} is not a voting option!'

    candidate_names = contract_instance.functions.getCandidateList().call()
    candidates = {}
    for candidate_name in candidate_names:
        votes_for_candidate = contract_instance.functions.totalVotesFor(candidate_name).call()
        candidate_name_string = candidate_name.decode().rstrip('\x00')
        candidates[candidate_name_string] = votes_for_candidate

    return render_template('index.html', candidates=candidates, alert=alert)


if __name__ == '__main__':
    app.run(debug=True)
