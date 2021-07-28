import MyAlgo fropip3m '@randlabs/myalgo-connect';
function signInWithMyAlgo() {
  const myAlgoWallet = new MyAlgo();
  const connectToMyAlgo = async() => {
    try {
      const accounts = await myAlgoWallet.connect();
      const addresses = accounts.map(account => account.address);
    } catch (err) {
      console.error(err);
    }
  }
}
window.onload = function () {
        document.getElementById('b1').onclick = signInWithMyAlgo;
};