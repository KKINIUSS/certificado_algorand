import MyAlgo from '@randlabs/myalgo-connect'
async function signInWithMyAlgo(e) {
        let asset_id = e.getAttribute('data-asset');
        const myAlgoWallet = new MyAlgo();
        const accounts = await myAlgoWallet.connect();
        var address = accounts[0].address
        let username = e.getAttribute('data-name')
        let data = []
        data.push({'address': address}, {'asset_id': asset_id}, {'name': username})
        console.log(data)
        $.ajax({
            url: "/claim_nft",
            dataType: "json",
            contentType : "application/json",
            data: JSON.stringify(data),
            type: 'POST',
            success: function (data) {
                console.log(data)
                if (data == 'Success') {
                    $('.msg-access').show('100');
                    document.querySelector('.content-msg').firstChild.textContent= "NFT-copy of your certificate was sent to your wallet.";
                    }
            }
        });
  }
window.create = async function create(e) {
        signInWithMyAlgo(e)
     };