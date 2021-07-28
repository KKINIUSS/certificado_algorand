import MyAlgo from '@randlabs/myalgo-connect'
async function signInWithMyAlgo(e) {
        let asset_id = e.getAttribute('data-asset');
        const myAlgoWallet = new MyAlgo();
        const accounts = await myAlgoWallet.connect();
        var adress = accounts[0].address
        let username = e.getAttribute('data-name')
        console.log(username)
        console.log(asset_id)
        console.log(adress)
        var xhr = new XMLHttpRequest();
        var body = 'assetid=' + encodeURIComponent(asset_id) +'&address=' + encodeURIComponent(adress) + '&name=' + encodeURIComponent(username);
        xhr.open("POST", '/claim_nft', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.send(body);
  }
window.create = async function create(e) {
        signInWithMyAlgo(e)
     };