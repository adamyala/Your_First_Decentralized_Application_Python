from testnet import contract_constructor, prepare_and_send_transaction


# the contract_constructor contains the data we need to put in the transaction
# the first few chunks on the data are instructions to deploy the rest of the data
transaction_details = contract_constructor.buildTransaction()

transaction_receipt = prepare_and_send_transaction(transaction_details)

# just because the transaction was accepted into the network, doesn't mean it was successful.
# after we get a receipt we check the status field. if its 1, the transaction was successful.
# if its 0 the transaction failed.
if transaction_receipt['status'] == 1:
    print('transaction successful')
    # now that our transaction is accepted, we use our transaction receipt to get the address
    # our contract we deployed to
    contract_address = transaction_receipt['contractAddress']

    # we'll need this contract address for running this flask app, so lets write it to a file
    with open('testnet/contract_address.txt', 'w') as file:
        file.write(contract_address)
else:
    print('transaction failed')
    # a transaction can fail for a number of reasons. if you're on the testnet and this
    # transaction keeps failing, try increasing the gas in build_transaction_base()
