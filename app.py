import datetime
import os.path
import random
import hashlib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template ,request, send_file, send_from_directory, jsonify
from algosdk import kmd, account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, PaymentTxn, AssetTransferTxn
import sqlite3
import csv
import json
from flask.helpers import url_for
from werkzeug.utils import redirect
import pdfkit
from werkzeug.utils import secure_filename
from platform import python_version

app = Flask(__name__)
UPLOAD_FOLDER = 'C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
from_email = 'certificado.supp@gmail.com'
password = 'eoomamwfjaurnpyc'

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
    pdfkit_options = {
        'orientation': 'landscape',
        'margin-bottom': '0in',
        'margin-left': '0in',
        'margin-right': '0in',
        'margin-top': '0in',
        'page-height': '12in',
        'page-width': '8in',
        'no-outline': None
    }
    stringer = str(datetime.datetime.now())
    hash = hashlib.sha1(stringer.encode('utf-8')).hexdigest()
    cn = ''.join(course.split())
    file_name = cn + "_" + str(hash)
    print(file_name)
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
        with open('C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % (str(file_name)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            send_amount = 10000 * len(student) + 100000 * len(student)
            existing_account = account_public_key
            send_to_address = address
            tx = PaymentTxn(existing_account, params, send_to_address, send_amount)
            signed_tx = tx.sign(account_private_key)
            try:
                tx_confirm = algod_client.send_transaction(signed_tx)
                print('Transaction sent with ID', signed_tx.transaction.get_txid())
                wait_for_confirmation(algod_client, txid=signed_tx.transaction.get_txid())
            except Exception as e:
                print(e)
            writer.writerow(["Student", "Access code", "Asset ID"])
            for i in student:
                asset_id = random.randint(10000000, 99999999)
                params = algod_client.suggested_params()
                params.fee = 1000
                params.flat_fee = True
                user_info = {'address': address, 'mnemonic': mnemonic_key}
                txn = AssetConfigTxn(
                    sender=str(user_info['address']),
                    sp=params,
                    total=1,
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
                stnx = txn.sign(mnemonic.to_private_key(user_info['mnemonic']))
                txid = algod_client.send_transaction(stnx)
                wait_for_confirmation(algod_client, txid)
                try:
                   ptx = algod_client.pending_transaction_info(txid)
                   asset_id = ptx["asset-index"]
                   global_asset_id = str(ptx["asset-index"])
                   print_created_asset(algod_client, user_info['address'], asset_id)
                   print_asset_holding(algod_client, user_info['address'], asset_id)
                except Exception as e:
                   print(e)
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                hash = random.randint(100000, 999999)
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template, access_code) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, str(asset_id), description, time, course, templates, str(hash)])
                con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, str(asset_id)), "certificates/{}.pdf".format(username + "_" + str(asset_id)), configuration=config, options=pdfkit_options)
                writer.writerow([i, str(hash), str(asset_id)])
            csvfile.close()
            print("File created")
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(from_email, password)
        msg = MIMEMultipart()
        filepath = 'C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % str(file_name)
        basename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        print("file success")
        part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename))
        part_file.set_payload(open(filepath, "rb").read())
        print("file success")
        part_file.add_header('Content-Description', basename)
        part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))
        encoders.encode_base64(part_file)
        message = '''
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/html">
    <head>
        <meta charset="utf-8">
        <style>
            * {
                margin: 0;
                padding: 0;
            }

        </style>
       </head>
<body>
    <div style="position: fixed; background-color: #060730; width: 100%; height: 100%;">
    <div style="margin-top: 3vh;
                width: 100%;
                height: 100px;"></div>
    <div style="margin-top: 5%;">
        <div style="margin: auto;
                border-radius: 3px;
                background-color: #fff;
                width: 70%;
                height: 30%;
                padding: 2%;">
            <span style="font-size: 2vh; color: #000;">
                Congratulations! Certificates for your students have been successfully issued on the Algorand blockchain.<br>

                Download the file with the access codes in the attachment.<br>

                To obtain certificates, go to the <a href="http://95.83.116.146:5000/validator"> Link </a> and enter the access codes.<br>
            </span>
        </div>
    </div>
    <div style="margin-top: 1%;">
        <div style="margin-top: 1%;
                margin: auto;
                padding: 2%;
                border-radius: 3px;
                background-color: #fff;
                width: 70%;
                height: 30%;">
            <span style="font-size: 2vh; color: #000;">
                If you want to get your NFT, please follow a few steps: <br>
                1) Register a wallet in Algorand <br>
                2) Your wallet balance must be at least 0.2 Algo <br>
                3) Add Asset with ID to your wallet. <br>
                4) Go to the <a href="http://95.83.116.146:5000/validator"> website </a> enter a name -> select a certificate -> enter "Access code" -> Claim NFT -> connect the wallet to the site. <br>
                <br>
                Victory! The NFT certificate will be transferred to your wallet.<br>
            </span>
        </div>
    </div>
    <div style="margin-top: 1%;">
        <div style="
                margin-top: 1%;
                margin: auto;
                border-radius: 3px;
                width: 70%;">
            <h1 style="color: #fff; text-align: center; font-size: 3vh;"> <br>Regards, Certificado Team! </h1>
            <img src="http://95.83.116.146:5000/static/logo.png" style="width: 20%; display: block; margin: 0 auto; padding: 30px 0;">
        </div>
    </div>
</body>
</html>'''
        subject = 'Certificate access codes'
        html = '<html><header></header><body><p>' + message + '</p></body></html>'
        part_html = MIMEText(html, 'html')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = email
        msg['Reply-To'] = from_email
        msg['Return-Path'] = from_email
        msg['X-Mailer'] = 'Python/' + (python_version())
        msg.attach(part_html)
        msg.attach(part_file)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()
        #return send_file('/home/kiselperdit/PycharmProjects/algorand/files/%s.csv' %(str(now)), as_attachment=False)
        return  jsonify("static/files/" + str(file_name) + ".csv")
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
        with open('C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % (str(file_name)), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(["Student", "Access code", "Asset ID"])
            send_amount = 200000 + 10000 * len(student) + 100000 * len(student)
            existing_account = account_public_key
            send_to_address = address
            tx = PaymentTxn(existing_account, params, send_to_address, send_amount)
            signed_tx = tx.sign(account_private_key)
            try:
                tx_confirm = algod_client.send_transaction(signed_tx)
                print('Transaction sent with ID', signed_tx.transaction.get_txid())
                wait_for_confirmation(algod_client, txid=signed_tx.transaction.get_txid())
            except Exception as e:
                print(e)
            for i in student:
                asset_id = random.randint(10000000, 99999999)
                params = algod_client.suggested_params()
                params.fee = 1000
                params.flat_fee = True
                user_info = {'address': address, 'mnemonic': mnemonic_key}
                txn = AssetConfigTxn(
                    sender=str(user_info['address']),
                    sp=params,
                    total=1,
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
                stnx = txn.sign(mnemonic.to_private_key(user_info['mnemonic']))
                txid = algod_client.send_transaction(stnx)
                wait_for_confirmation(algod_client, txid)
                try:
                   ptx = algod_client.pending_transaction_info(txid)
                   asset_id = ptx["asset-index"]
                   global_asset_id = str(ptx["asset-index"])
                   print_created_asset(algod_client, user_info['address'], asset_id)
                   print_asset_holding(algod_client, user_info['address'], asset_id)
                except Exception as e:
                   print(e)
                time = datetime.datetime.now()
                time = time.strftime("%d/%m/%Y")
                hash = random.randint(100000, 999999)
                cur.execute("insert into certificates (path, student, school, asset_id, description, date, course_name, template, access_code) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", ['', i, email, str(asset_id), description, time, course, templates, str(hash)])
                con.commit()
                username_mas = i.split()
                username = '_'.join(username_mas)
                pdfkit.from_url("http://127.0.0.1:5000/get_certificate/%s/%s/%s" %(username, hash, str(asset_id)), "certificates/{}.pdf".format(username + "_" + str(asset_id)), configuration=config, options=pdfkit_options)
                writer.writerow([i, str(hash), str(asset_id)])
            csvfile.close()
            print("File created")
        cur.execute("insert into accounts (email, address, private_key, mnemonic) values (?, ?, ?, ?)", [ email, address, private_key, mnemonic_key])
        con.commit()
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(from_email, password)
        msg = MIMEMultipart()
        filepath = 'C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\static\\files\\%s.csv' % str(file_name)
        basename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        print("file success")
        part_file = MIMEBase('application', 'octet-stream; name="{}"'.format(basename))
        part_file.set_payload(open(filepath, "rb").read())
        print("file success")
        part_file.add_header('Content-Description', basename)
        part_file.add_header('Content-Disposition', 'attachment; filename="{}"; size={}'.format(basename, filesize))
        encoders.encode_base64(part_file)
        message = '''
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/html">
            <head>
                <meta charset="utf-8">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                    }

                </style>
               </head>
        <body>
            <div style="position: fixed; background-color: #060730; width: 100%; height: 100%;">
            <div style="margin-top: 3vh;
                        width: 100%;
                        height: 100px;"></div>
            <div style="margin-top: 5%;">
                <div style="margin: auto;
                        border-radius: 3px;
                        background-color: #fff;
                        width: 70%;
                        height: 30%;
                        padding: 2%;">
                    <span style="font-size: 2vh; color: #000;">
                        Congratulations! Certificates for your students have been successfully issued on the Algorand blockchain.<br>

                        Download the file with the access codes in the attachment.<br>

                        To obtain certificates, go to the <a href="http://95.83.116.146:5000/validator"> Link </a> and enter the access codes.<br>
                    </span>
                </div>
            </div>
            <div style="margin-top: 1%;">
                <div style="margin-top: 1%;
                        margin: auto;
                        padding: 2%;
                        border-radius: 3px;
                        background-color: #fff;
                        width: 70%;
                        height: 30%;">
                    <span style="font-size: 2vh; color: #000;">
                        If you want to get your NFT, please follow a few steps: <br>
                        1) Register a wallet in Algorand <br>
                        2) Your wallet balance must be at least 0.2 Algo <br>
                        3) Add Asset with ID to your wallet. <br>
                        4) Go to the <a href="http://95.83.116.146:5000/validator"> website </a> enter a name -> select a certificate -> enter "Access code" -> Claim NFT -> connect the wallet to the site. <br>
                        <br>
                        Victory! The NFT certificate will be transferred to your wallet.<br>
                    </span>
                </div>
            </div>
            <div style="margin-top: 1%;">
                <div style="
                        margin-top: 1%;
                        margin: auto;
                        border-radius: 3px;
                        width: 70%;">
                    <h1 style="color: #fff; text-align: center; font-size: 3vh;"> <br>Regards, Certificado Team! </h1>
                    <img src="http://95.83.116.146:5000/static/logo.png" style="width: 20%; display: block; margin: 0 auto; padding: 30px 0;">
                </div>
            </div>
        </body>
        </html>'''
        subject = 'Certificate access codes'
        html = '<html><header></header><body><p>' + message + '</p></body></html>'
        part_html = MIMEText(html, 'html')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = email
        msg['Reply-To'] = from_email
        msg['Return-Path'] = from_email
        msg['X-Mailer'] = 'Python/' + (python_version())
        msg.attach(part_html)
        msg.attach(part_file)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()
        return  jsonify("static/files/" + str(file_name) + ".csv")

#def send_files(filename):
#    print(filename)
#    return redirect(url_for('static',filename='join.html'))
#    return send_from_directory('/home/kiselperdit/PycharmProjects/algorand/static/files', filename + ".csv", as_attachment=False)
@app.route("/certificates/example_template.jpg", methods=["GET", "POST"])
def download_example():
    return send_from_directory('C:\\Users\\Fiji\\PycharmProjects\\pythonProject\\certificado_algorand\\certificates', 'example_template.jpg', as_attachment=False)

@app.route("/get_certificate/<name>/<code>/<asset>", methods=["GET", "POST"])
def certificate(name, code, asset):
    print(name, code, asset)
    code = ''.join(code.split())
    name = ' '.join(name.split("_"))
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    cur.execute("select template, school, description from certificates where asset_id=? and student=? and access_code=?", [asset, name, code])
    temp = cur.fetchall()
    print(temp)
    if(temp[0][0]):
        if(temp[0][0] != 'on'):
            if(temp[0][0] == '3'):
                return render_template("index.html", name=name, back= "/static/" + temp[0][0] + ".png", link="http://95.83.116.146:5000/validate/" + asset, style=' #000000', description= temp[0][2])
            else:
                return render_template("index.html", name=name, back= "/static/" + temp[0][0] + ".png", link="http://95.83.116.146:5000/validate/" + asset, style=' #ffffff', description= temp[0][2])
        else:
            filename = temp[0][1]
            filename = ''.join(filename.split('@'))
            return render_template("index.html", name=name, back="/static/img/" + filename + '_template.png', link="http://95.83.116.146:5000/validate/" + asset, style=' #ffffff', description= temp[0][2])
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
        cur.execute("select * from certificates where student=?", [name])
        certificates = cur.fetchall()
        print(certificates)
        print(1)
        return jsonify(certificates)
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
    print(address)
    name = request.form.get("name")
    print(name, asset_id)
    cur.execute("select school from certificates where asset_id=? and student=?", [asset_id, name])
    email_school = cur.fetchall()
    print(email_school[0][0])
    cur.execute("select * from accounts where email=?", [email_school[0][0]])
    req_ = cur.fetchall()
    cur.execute("select mnemonic, address from accounts where email=?", [email_school[0][0]])
    querry = cur.fetchall()
    print(querry, req_)
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    algod_token = "ygZS35fp3q95Hgl64Ga4d8ZsINOqYGB15UdsA5Cr"
    purestake_token = {'X-Api-key': algod_token}
    algod_client = algod.AlgodClient(algod_token=algod_token, algod_address=algod_address, headers=purestake_token)
    public_key = mnemonic.to_public_key(querry[0][0])
    private_key = mnemonic.to_private_key(querry[0][0])
    address_sender = req_[0][1]
    print(public_key)
    private_key_sender = req_[0][2]
    params = algod_client.suggested_params()
    print("success")
    params.fee = 1000
    params.flat_fee = True
    txn = AssetTransferTxn(
        sender=public_key,
        sp=params,
        receiver=address,
        amt=1,
        index=asset_id)
    stxn = txn.sign(private_key_sender)
    txid = algod_client.send_transaction(stxn)
    return jsonify(req_)

@app.route("/validate/<asset_id>", methods=["GET"])
def validate(asset_id):
    algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
    algod_token = "ygZS35fp3q95Hgl64Ga4d8ZsINOqYGB15UdsA5Cr"
    purestake_token = {'X-Api-key': algod_token}
    algod_client = algod.AlgodClient(algod_token=algod_token, algod_address=algod_address, headers=purestake_token)
    con = sqlite3.connect("example.db")
    cur = con.cursor()
    cur.execute("select school, course_name, student from certificates where asset_id=?", [asset_id])
    school = cur.fetchall()
    mn = "bamboo minimum topple olympic isolate moon picture notable execute soap great output path scale security include west present zone bundle crawl squirrel seat about tent"
    if(school):
        print_asset_holding(algod_client, mnemonic.to_public_key(mn), asset_id)
        return render_template("auth.html", desc = school[0][1], name=school[0][2], link="https://algoexplorer.io/asset/" + asset_id)

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
        print(q)
        if(q):
            print(q[0][0])
            return jsonify('/download_certificate/' + str(data[1]['aseet-id'] + '/' + q[0][0]), q[0][0])
        else:
            return "Error"
if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)