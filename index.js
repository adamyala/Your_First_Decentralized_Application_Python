const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
const VotingContract = web3.eth.contract(abi);
const contractInstance = VotingContract.at(contractAddress);
const candidates = {"Rama": "candidate-1", "Nick": "candidate-2", "Jose": "candidate-3"};

function voteForCandidate() {
  const candidateName = $("#candidate").val();
  contractInstance.voteForCandidate(candidateName, {from: web3.eth.accounts[0]}, function() {
    let div_id = candidates[candidateName];
    $("#" + div_id).html(contractInstance.totalVotesFor.call(candidateName).toString());
  });
}

$(document).ready(function() {
  const candidateNames = Object.keys(candidates);
  for (let i = 0; i < candidateNames.length; i++) {
    let name = candidateNames[i];
    let val = contractInstance.totalVotesFor.call(name).toString();
    $("#" + candidates[name]).html(val);
  }
});