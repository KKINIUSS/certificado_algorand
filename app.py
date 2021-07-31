import datetime
import os.path
import random
import hashlib
from flask import Flask, render_template ,request, send_file, send_from_directory, jsonify
from algosdk import kmd, account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, PaymentTxn
import sqlite3
import csv
import json
from flask.helpers import url_for
from werkzeug.utils import redirect
import pdfkit
from werkzeug.utils import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER = 'C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo

def print_created_asset(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0;
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['index'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break

def print_asset_holding(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break

@app.route("/", methods=["GET"])
def index():
    return render_template("join_withoutPopUp.html")

@app.route("/join", methods=["POST"])
def api():
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    algod_token = "ygZS35fp3q95Hgl64Ga4d8ZsINOqYGB15UdsA5Cr"
    purestake_token = {'X-Api-key': algod_token}
    algod_client = algod.AlgodClient(algod_token=algod_token, algod_address=algod_address, headers=purestake_token)
    mnemonic_sender = "bamboo minimum topple olympic isolate moon picture notable execute soap great output path scale security include west present zone bundle crawl squirrel seat about tent"
    account_private_key = mnemonic.to_private_key(mnemonic_sender)    
    account_public_key = mnemonic.to_public_key(mnemonic_sender)
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    print(1)
    data = request.get_json()
    print(data)
    email = data[0]['value']
    course = data[1]['value']
    templates = data[2]['value']
    description = data[3]['value']
    print(email, course, templates, description)
    student = (data[4]['value']).split('\r\n')
    print(email, course, templates, description, student)
    cur.execute("create table if not exists accounts (email text, address text,private_key text, mnemonic text)")
    cur.execute("create table if not exists student (name text, code text)")
    cur.execute("create table if not exists certificates (path text, student text, school text, asset_id text, description text, date, course_name text, template text, access_code)")
    con.commit()
    cur.execute("select address, mnemonic from accounts where email=?", [email])
    query = cur.fetchall()
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    if(query):  
        address = query[0][0]
        mnemonic_key = query[0][1]
        print(address, mnemonic_key)
        params = algod_client.suggested_params()
        gh = params.gh
        first_valid_round = params.first
        last_valid_round = params.last
        fee = params.min_fee
        params.flat_fee = True
        params.fee = 1000
        send_amount = 200000 + 10000 * len(student)
        print(send_amount)
        existing_account = account_public_key
        send_to_address = address
        #tx = transaction.PaymentTxn(existing_account, params, send_to_address, send_amount)
        #signed_tx = tx.sign(account_private_key)
        #try:
        #    tx_confirm = algod_client.send_transaction(signed_tx)
        #    print('Transaction sent with ID', signed_tx.transaction.get_txid())
        #    wait_for_confirmation(algod_client, txid=signed_tx.transaction.get_txid())
        #except Exception as e:
        #    print(e)
        params = algod_client.suggested_params()
        params.fee = 1000
        params.flat_fee = True
        stringer = str(datetime.datetime.now())
        hash = hashlib.sha1(stringer.encode('utf-8')).hexdigest()
        cn = ''.join(course.split())
        now = cn + "_" + str(hash)
        user_info = {'address' : address, 'mnemonic' : mnemonic_key}
        txn = AssetConfigTxn(
            sender=str(user_info['address']),
            sp=params,
            total=len(student),
            default_frozen=False,
            unit_name="CFTCD",
            asset_name=course,
            manager=str(user_info['address']),
            reserve=str(user_info['address']),
            freeze=str(user_info['address']),
            clawback=str(user_info['address']),
            url="https://certificado.one",
            note=description,
            decimals=0)
        #stnx = txn.sign(mnemonic.to_private_key(user_info['mnemonic']))
        #txid = algod_client.send_transaction(stnx)
        #wait_for_confirmation(algod_client, txid)
        global_asset_id = ''
        #try:
        #    ptx = algod_client.pending_transaction_info(txid)
        #    asset_id = ptx["asset-index"]
        #    global_asset_id = str(ptx["asset-index"])
        #    print_created_asset(algod_client, user_info['address'], asset_id)
        #    print_asset_holding(algod_client, user_info['address'], asset_id)
        #except Exception as e:
        #    print(e)
        with open('C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % (str(now)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["Студент", "Код доступа к поиску", "Код доступа к сертификату"])
            for i in student:
                cur.execute("select code from student where name=?", [i])
                code = cur.fetchall()
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                if(code):
                    hash = code[0][0]
                else:
                    hash = random.randint(100000, 999999)
                    cur.execute("insert into student (name, code) values (?, ?)", [i, hash])
                    con.commit()
                hash_1 = random.randint(1000000, 9999999)
                asset_id = random.randint(1000000, 9999999)
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template, access_code) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, str(asset_id), description, time, course, templates, str(hash_1)])
                con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, str(asset_id)), "certificates/{}.pdf".format(username + "_" + str(asset_id)), configuration=config)
                writer.writerow([i, str(hash), str(hash_1)])
            csvfile.close()
        #return send_file('/home/kiselperdit/PycharmProjects/algorand/files/%s.csv' %(str(now)), as_attachment=False)
        return  jsonify("static/files/" + str(now) + ".csv")
    else:
        private_key, address = account.generate_account()
        mnemonic_key = mnemonic.from_private_key(private_key)
        print(private_key, address, mnemonic_key)
        params = algod_client.suggested_params()
        gh = params.gh
        first_valid_round = params.first
        last_valid_round = params.last
        fee = params.min_fee
        params.flat_fee = True
        params.fee = 1000
        send_amount = 200000 + 10000 * len(student)
        existing_account = account_public_key
        send_to_address = address
        #tx = transaction.PaymentTxn(existing_account, params, send_to_address, send_amount)
        #signed_tx = tx.sign(account_private_key)

        #try:
        #    tx_confirm = algod_client.send_transaction(signed_tx)
        #    print('Transaction sent with ID', signed_tx.transaction.get_txid())
        #    wait_for_confirmation(algod_client, txid=signed_tx.transaction.get_txid())
        #except Exception as e:
        #    print(e)
        params = algod_client.suggested_params()
        params.fee = 1000
        params.flat_fee = True
        stringer = str(datetime.datetime.now())
        hash = hashlib.sha1(stringer.encode('utf-8')).hexdigest()
        cn = ''.join(course.split())
        now = cn + "_" + str(hash)
        user_info = {'address' : address, 'mnemonic' : mnemonic_key}
        txn = AssetConfigTxn(
            sender=str(user_info['address']),
            sp=params,
            total=len(student),
            default_frozen=False,
            unit_name="CFTCD",
            asset_name=course,
            manager=str(user_info['address']),
            reserve=str(user_info['address']),
            freeze=str(user_info['address']),
            clawback=str(user_info['address']),
            url="https://certificado.one",
            note=description,
            decimals=0)
        #stnx = txn.sign(mnemonic.to_private_key(user_info['mnemonic']))
        #txid = algod_client.send_transaction(stnx)
        #wait_for_confirmation(algod_client, txid)
        global_asset_id = ''
        #try:
        #    ptx = algod_client.pending_transaction_info(txid)
        #    asset_id = ptx["asset-index"]
        #    global_asset_id = str(ptx["asset-index"])
        #    print_created_asset(algod_client, user_info['address'], asset_id)
        #    print_asset_holding(algod_client, user_info['address'], asset_id)
        #except Exception as e:
        #    print(e)
        with open('C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % (str(now)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["Студент", "Код доступа к поиску", "Код доступа к сертификату"])
            for i in student:
                cur.execute("select code from student where name=?", [i])
                code = cur.fetchall()
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                if (code):
                    hash = code[0][0]
                else:
                    hash = random.randint(100000, 999999)
                    cur.execute("insert into student (name, code) values (?, ?)", [i, hash])
                    con.commit()
                hash_1 = random.randint(100000, 999999)
                asset_id = random.randint(1000000, 9999999)
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template, access_code) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, str(asset_id), description, time, course, templates, str(hash_1)])
                con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, str(asset_id)), "certificates/{}.pdf".format(username + "_" + str(asset_id)), configuration=config)
                writer.writerow([i, str(hash), str(hash_1)])
            csvfile.close()
        cur.execute("insert into accounts (email, address, private_key, mnemonic) values (?, ?, ?, ?)", [ email, address, private_key, mnemonic_key])
        con.commit()
        return  jsonify("static/files/" + str(now) + ".csv")

#def send_files(filename):
#    print(filename)
#    return redirect(url_for('static',filename='join.html'))
#    return send_from_directory('/home/kiselperdit/PycharmProjects/algorand/static/files', filename + ".csv", as_attachment=False)

@app.route("/get_certificate/<name>/<code>/<asset>", methods=["GET", "POST"])
def certificate(name, code, asset):
    print(1)
    print(name, code, asset)
    code = ''.join(code.split())
    name = ' '.join(name.split("_"))
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    cur.execute("select template, school from certificates where asset_id=? and student=?", [asset, name])
    temp = cur.fetchall()
    cur.execute("select * from student where name=? and code=?", [str(name), str(code)])
    req_ = cur.fetchall()
    print(req_ )
    print(temp)
    if(req_[0][0] and temp[0][0]):
        if(temp[0][0] != 'on'):
            return render_template("index.html", name=name, back= "/static/" + temp[0][0] + ".png", link="http://localhost:5000/")
        else:
            filename = temp[0][1]
            filename = ''.join(filename.split('@'))
            return render_template("index.html", name=name, back="/static/img/" + filename + '_template.png', link="https://google.com")
    else:
        return "Ошибка"

@app.route("/upload_template", methods=["GET", "POST"])
def upload():
    file = request.files['myFile']
    file_name = request.form.get('email')
    file_name = ''.join(file_name.split('@'))
    print(file_name)
    filename = secure_filename(file_name + '_template.png')
    print(filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(1)
    return "1"
@app.route("/validator", methods=["GET", "POST"])
def validator():
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    data = request.get_json()
    if(data):
        print(data)
        name = data[0]['value']
        code = data[1]['value']
        print(name, code)
        code = ''.join(code.split())
        cur.execute("select * from student where name=? and code=?", [name, code])
        _request = cur.fetchall()
        if(_request):
            print(len(_request))
            if(len(_request) == 1):
                cur.execute("select * from certificates where student=?", [name])
                certificates = cur.fetchall()
                print(certificates)
                return jsonify(certificates)
            else:
                cur.execute("select * from certificates where student=?", [name])
                certificates = cur.fetchall()
                print(certificates)
                return str(1234)
        else:
            print(_request)
            return str(12)
    else:
        return render_template("result.html")

@app.route('/download_certificate/<asset_id>/<name>', methods=["GET", "POST"])
def download_certificate(asset_id, name):
    print(name, asset_id)
    name = '_'.join(name.split())
    print(name)
    return send_from_directory("C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\certificates", name + "_" + asset_id + ".pdf", as_attachment=False)

@app.route('/download/<filename>', methods=["GET", "POST"])
def download(filename):
    print(filename)
    return send_from_directory("C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files", filename, as_attachment=False)

@app.route("/claim_nft", methods=["POST"])
def transaction():
    print(1)
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    mas = []
    asset_id = request.form.get("assetid")
    address = request.form.get("address")
    name = request.form.get("name")
    print(name, asset_id)
    cur.execute("select school from certificates where asset_id=? and student=?", [asset_id, name])
    email_school = cur.fetchall()
    print(email_school[0][0])
    cur.execute("select * from accounts where email=?", [email_school[0][0]])
    req_ = cur.fetchall()
    address_sender = req_[0][1]
    private_key_sender = req_[0][2]
    return jsonify(req_)
#    params = algod_client.suggested_params()
#    params.fee = 1000
#    params.flat_fee = True
#    txn = AssetTransferTxn(
#        sender=accounts[1]['pk'],
#        sp=params,
#        receiver=accounts[3]["pk"],
#        amt=1,
#        index=asset_id)
#    stxn = txn.sign(accounts[1]['sk'])
#    txid = algod_client.send_transaction(stxn)
#    print(txid)
#    # Wait for the transaction to be confirmed
#    wait_for_confirmation(algod_client, txid)
#    # The balance should now be 10.
#print_asset_holding(algod_client, accounts[3]['pk'], asset_id)

@app.route("/access", methods=["POST"])
def access():
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    data = request.get_json()
    print(data)
    data[0]['value'] = ''.join(data[0]['value'].split())
    if(data[0]['value'] and data[1]['aseet-id']):
        cur.execute("select * from certificates")
        print(cur.fetchall())
        cur.execute("select student from certificates where access_code=? and asset_id=?", [data[0]['value'], data[1]['aseet-id']])
        q = cur.fetchall()
        if(q):
            print(q[0][0])
            return jsonify('/download_certificate/' + str(data[1]['aseet-id'] + '/' + q[0][0]), q[0][0])
        else:
            return "Error"
if __name__ == "__main__":
    app.run(debug=True)