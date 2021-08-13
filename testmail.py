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
from threading import  Thread

str = "teach, predict, fault, claw, reveal, will, crystal, bread, wrap, meadow, achieve, spend, donate, awake, mimic, grocery, sample, pizza, frost, sentence, fire, guilt, acid, abandon, weekend"

print(' '.join(str.split(',')))