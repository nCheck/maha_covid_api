import flask
import os
from flask import jsonify, request , make_response
from flask import flash, redirect, url_for, session , render_template
from flask_cors import CORS, cross_origin
import requests, json
import pandas as pd
import requests
import json 
from datetime import datetime, timedelta

#get useful funcs
from logic import checkIfLatest , downloadPdf , covidapidb , testcol , old_data_col , latest_data_col




app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'super secret key'
cors = CORS(app, resources={r"/*": {"origins": "*"}})


#get key value for districts
id_dist = None
with open('id_dist_pair.json', 'r') as fp:
    id_dist = json.load(fp)


@app.route('/test', methods=['GET','POST'])
def test():
    print("I'm running" , testcol.find_one({}))
    data = [ 1 , 2 , "Buckle My Shoe" , 3 , 4 , "Shut the Door" ]
    return jsonify( data )


@app.route('/test_tabula', methods=['GET'])
def test_tabula():
    print("I'm running" , testcol.find_one({}))
    data = [ 1 , 2 , "Buckle My Shoe" , 3 , 4 , "Shut the Door" ]
    return jsonify( data )


@app.route('/latest', methods=['GET'])
def latest():
    # checkIfLatest()
    data = latest_data_col.find_one({})
    data = { "data" : data['stats'] , "last_updated" : data['date'] }
    return jsonify( data )


@app.route('/all', methods=['GET'])
def get_all():
    data = old_data_col.find({})
    resp = []
    for d in data:
        resp.append( { "data" : d['stats'] , "date" : d['date'] } )
    
    return jsonify( resp )



@app.route('/update_trigger', methods=['GET'])
def update_trigger():
    resp = checkIfLatest()
    return jsonify(resp)


@app.route('/ids', methods=['GET'])
def getKeyValue():
    return jsonify(id_dist)

@app.route('/history/<id>', methods=['GET'])
def district_history(id):

    sort_d_history = district_history_util(id)

    return jsonify(sort_d_history)

@app.route('/', methods=['GET'])
def home():
    data = latest_data_col.find_one({})
    last_updated = data['date']
    data = data['stats']
    rows = []

    _dist_id = {v: k for k, v in id_dist.items()}

    cols = [ 'District/Municipal' , 'TOTAL CASES' , 'NEW CASES' , 'TOTAL DEATHS' , 'NEW DEATHS']
    for d in data.keys():

        rows.append( { 'district': d , 'total_cases' : data[d]['TOTAL_CASES'] , 
                    'new_cases' : data[d]['NEW_CASES'] , 'total_deaths' : data[d]['TOTAL_DEATHS'] , 
                    'new_deaths' : data[d]['NEW_DEATHS'] , 'recovered' : data[d]['RECOVERED'] , 'url' : '/graph/' + _dist_id[d] } )



    print(rows[0])
    print(rows[1])

    return render_template('start.html' , rows=rows , cols = cols , last_updated = last_updated)


@app.route('/graph/<id>', methods=['GET'])
def graph(id='1'):
    data = district_history_util(id)
    new_cases = []
    total_cases = []
    recovered_cases = []
    for i , d in  enumerate( data ):
        new_cases.append( { "x" : i , "y" : d['NEW_CASES'] } )
        total_cases.append( { "x" : i , "y" : d['TOTAL_CASES'] - d['RECOVERED']  } )
        recovered_cases.append( { "x" : i , "y" : d['RECOVERED'] } )
    
    new_cases = json.dumps(new_cases)
    total_cases = json.dumps(total_cases)
    recovered_cases = json.dumps(recovered_cases)

    return render_template('line_graph.html' , new_cases = new_cases , total_cases = total_cases , recovered_cases = recovered_cases , dist = id_dist[id])



def district_history_util(id):
    district = id_dist[id]
    data = old_data_col.find({})
    fourteen_days_date = datetime.today() - timedelta(days=15)
    d_history = []

    for d in data:
        stat = d['stats'][district]
        date = d['date']
        if date > fourteen_days_date and 'NEW_CASES' in stat.keys():

            for ks in stat.keys():
                try:
                    stat[ks] = int( stat[ks] )
                except:
                    spl = ((str(stat[ks])).split(' '))[0]
                    stat[ks] = int(spl)


            stat['date'] = date
            d_history.append(stat)

    sort_d_history = sorted(d_history, key = lambda i: i['date'])

    return sort_d_history

if __name__ == '__main__':
    app.run()