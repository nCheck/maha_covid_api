import flask
import os
from flask import jsonify, request
from flask import flash, redirect, url_for, session
from flask_cors import CORS, cross_origin
import requests, json
import pandas as pd
import requests


#get useful funcs
from logic import checkIfLatest , downloadPdf , covidapidb , testcol , old_data_col , latest_data_col




app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'super secret key'
cors = CORS(app, resources={r"/*": {"origins": "*"}})







@app.route('/test', methods=['GET','POST'])
def test():
    print("I'm running" , testcol.find_one({}))
    data = [ 1 , 2 , "Buckle My Shoe" , 3 , 4 , "Shut the Door" ]
    return jsonify( data )


@app.route('/latest', methods=['GET'])
def latest():
    checkIfLatest()
    data = latest_data_col.find_one({})
    data = { "data" : data['stats'] , "last_updated" : data['date'] }
    return jsonify( data )









@app.route('/', methods=['GET'])
def home():
    print("loaded")
    return "Welcome to My API"




if __name__ == '__main__':
    app.run()