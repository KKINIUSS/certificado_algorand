import datetime
from os import link, name
import random
import hashlib
import re
from algosdk.future import transaction
from flask import Flask, render_template ,request, send_file, send_from_directory, jsonify
from algosdk import kmd, account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, PaymentTxn
import sqlite3
import csv
import json
from flask.helpers import url_for
import pdfkit
from algosdk.wallet import Wallet
from werkzeug.utils import redirect
from time import sleep
from werkzeug.wrappers import response
import pdfkit
app = Flask(__name__)

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
    print(1)
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    algod_token = "ygZS35fp3q95Hgl64Ga4d8ZsINOqYGB15UdsA5Cr"
    purestake_token = {'X-Api-key': algod_token}
    algod_client = algod.AlgodClient(algod_token=algod_token, algod_address=algod_address, headers=purestake_token)
    mnemonic_sender = "bamboo minimum topple olympic isolate moon picture notable execute soap great output path scale security include west present zone bundle crawl squirrel seat about tent"
    account_private_key = mnemonic.to_private_key(mnemonic_sender)    
    account_public_key = mnemonic.to_public_key(mnemonic_sender)
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    email = request.form.get("email")
    course = request.form.get("name")
    templates = request.form.get("theme")
    print(templates)
    course_unit_name = email 
    description = request.form.get("title")
    student = (request.form.get("student")).split('\r\n')
    print(student)
    cur.execute("create table if not exists accounts (email text, address text,private_key text, mnemonic text)")
    cur.execute("create table if not exists student (name text, code text)")
    cur.execute("create table if not exists certificates (path text, student text, school text, asset_id text, description text, date, course_name text, template text)")
    con.commit()
    cur.execute("select address, mnemonic from accounts where email=?", [email])
    query = cur.fetchall()
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
        with open('/home/kiselperdit/PycharmProjects/algorand/static/files/%s.csv' % (str(now)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["Студент", "Код доступа"])
            for i in student:
                cur.execute("select code from student where name=?", [i])
                code = cur.fetchall()
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template) values(?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, 'global_asset_id', description, time, course, templates])
                con.commit()
                if(code):
                    hash = code[0][0]
                else:
                    hash = random.randint(100000, 999999)
                    cur.execute("insert into student (name, code) values (?, ?)", [i, hash])
                    con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, 'global_asset_id'), "certificates/{}.pdf".format(username + "_" + 'global_asset_id'))
                writer.writerow([i, str(hash)])
            csvfile.close()
        #return send_file('/home/kiselperdit/PycharmProjects/algorand/files/%s.csv' %(str(now)), as_attachment=False)
        send_files(str(now))
        print(1)
        sleep(2)
        return render_template("join.html", name_file=str(now))
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
        with open('/home/kiselperdit/PycharmProjects/algorand/static/files/%s.csv' % (str(now)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["Студент", "Код доступа"])
            for i in student:
                cur.execute("select code from student where name=?", [i])
                code = cur.fetchall()
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template) values(?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, 'global_asset_id', description, time, course, templates])
                con.commit()
                if (code):
                    hash = code[0][0]
                else:
                    hash = random.randint(100000, 999999)
                    cur.execute("insert into student (name, code) values (?, ?)", [i, hash])
                    con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, 'global_asset_id'), "certificates/{}.pdf".format(username + "_" + 'global_asset_id'))
                writer.writerow([i, str(hash)])
            csvfile.close()
        cur.execute("insert into accounts (email, address, private_key, mnemonic) values (?, ?, ?, ?)", [ email, address, private_key, mnemonic_key])
        con.commit()
        #return send_file('/home/kiselperdit/PycharmProjects/algorand/files/%s.csv' %(str(now)), as_attachment=False)
        return render_template("join.html", name_file=str(now))

def send_files(filename):
    print(filename)
    return redirect(url_for('static',filename='join.html'))
    return send_from_directory('/home/kiselperdit/PycharmProjects/algorand/static/files', filename + ".csv", as_attachment=False)

@app.route("/get_certificate/<name>/<code>/<asset>", methods=["GET", "POST"])
def certificate(name, code, asset):
    print(1)
    print(name, code, asset)
    code = ''.join(code.split())
    name = ' '.join(name.split("_"))
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    cur.execute("select template from certificates where asset_id=? and student=?", [asset, name])
    temp = cur.fetchall()
    cur.execute("select * from student where name=? and code=?", [str(name), str(code)])
    req_ = cur.fetchall()
    print(req_ )
    print(temp)
    if(req_[0][0] and temp[0][0]):
        return render_template("index.html", name=name, back= "/static/" + temp[0][0] + ".png", link="https://google.com")
    else:
        return "Ошибка"

@app.route("/validator", methods=["GET"])
def validator():
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    name = request.args.get("name")
    code = request.args.get("code")
    if(name or code):
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
            return render_template("result-empty.html")
    else:
        return render_template("result.html")

@app.route('/download_certificate/<asset_id>/<name>', methods=["GET", "POST"])
def download_certificate(asset_id, name):
    print(name, asset_id)
    name = '_'.join(name.split())
    return send_from_directory("/home/kiselperdit/PycharmProjects/algorand/certificates", name + "_" + asset_id + ".pdf", as_attachment=False)

@app.route('/download/<filename>', methods=["GET", "POST"])
def download(filename):
    print(filename)
    return send_from_directory("/home/kiselperdit/PycharmProjects/algorand/static/files", filename, as_attachment=False)

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
if __name__ == "__main__":
    app.run(debug=True)