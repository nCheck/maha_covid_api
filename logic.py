import requests
import subprocess
import re
#Twitter API
import tweepy
import csv
import pandas as pd
from datetime import datetime
import tabula
import json
import os
from pymongo import MongoClient
####input your credentials here


mykeys = None
MONGO_URL = None
try:
    # server = os.environ['server']
    consumer_key = os.environ['consumer_key']
    consumer_secret = os.environ['consumer_secret']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']
    MONGO_URL = os.environ['mongodb_url']
except:

    print("no server")
    with open('keys.json') as f:
        mykeys = json.load(f)

    consumer_key = mykeys['twitter']['consumer_key']
    consumer_secret = mykeys['twitter']['consumer_secret']
    access_token = mykeys['twitter']['access_token']
    access_token_secret = mykeys['twitter']['access_token_secret']
    MONGO_URL = mykeys['mongodb']['url']

print( "MY KEYS" ,  (consumer_key, consumer_secret) , (access_token, access_token_secret) )

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#DATABASE

client = MongoClient(MONGO_URL)
covidapidb = client.covidapi
testcol = covidapidb.get_collection('test')
old_data_col = covidapidb.get_collection('old_data')
latest_data_col = covidapidb.get_collection('latest_data')

"""
The Functions
"""
def num_name(word):
  try:
    word = word.strip(" ")
    words = word.split(" ")
    # print(words)
    if len(words) == 1:
      return [None , words[0]]
    elif len(words) > 5:
      return [None , word]

    num = words[0]
    name = ' '.join( words[1:] )

    return [num , name]
  except:
    return [None , None]

def oldPdfToCsv(inp_file):
  top = 60
  left = 40
  width = 744
  height = 912

  y1 = top
  x1 = left
  y2 = top + height
  x2 = left + width


  out_file = 'out2.csv'

  tabula.convert_into( inp_file , out_file ,  stream=True  , output_format='csv', pages="11" )

  df = pd.read_csv('out2.csv' , header=None)
  # df.Name.apply(lambda x: pd.Series(str(x).split("_")))

  ndf = df[0].apply( lambda x : pd.Series( num_name(x) ) )
  ndf[[2,3,4,5,6]] = df[[1,2,3,5,6]]
  ndf.to_csv('out2.csv',index=False,header=False)


def getReportTweets(username = 'Maha_MEDD'):

  query = "A daily comprehensive report prepared by MEDD, Maharashtra showing #COVIDー19 situation in the state"
  tweets = api.user_timeline(screen_name=username , tweet_mode="extended" , count = 100)
  resp = {}
  for t in tweets:
    if not t.retweeted and 'RT @' not in t.full_text and query in t.full_text :
      resp[t.created_at]  =   { 'url' : t.entities['urls'][0]['expanded_url']  ,  'text' : t.full_text } 
      # resp.append(t)
  
  return resp


def getDicFromDfLoc(df_loc , date = None):
  
  if date is None:
    name = df_loc
    name = '-'.join(name.split('/')[1].split('.')[0].split('_')[1:])
    date = datetime.strptime(name, '%d-%m-%Y')

  df = pd.read_csv(df_loc, header=0 , index_col="DISTRICT/CORPORATION")
  # print(df.head())
  print("doing", df_loc)
  df.index.get_loc('TOTAL')
  ndata = df.head(57)
  ndata = ndata.fillna(0)
  data_dic = ndata.to_dict('index')
  return {"stats" : data_dic , "date" : date}


def downloadPdf(url , filename = 'demo.pdf'):
  fileid = url.split('/d/')[1].split('/')[0]

  comm = "wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=%s' -O 'pdfs/%s'"

  out = subprocess.call( comm%(fileid,filename) , shell=True )
  if out == 0:
    print("File Downloaded")
  else:
    print("Download Error")


def pdfToCsv( filename , old = False ):

  top = 85
  left = 40
  width = 744
  height = 912

  y1 = top
  x1 = left
  y2 = top + height
  x2 = left + width


  inp_file = "pdfs/" + filename

  #Read Page 10
  out_file = 'out1.csv'

  tabula.convert_into( inp_file , out_file ,  lattice=True , area =[y1 , x1  , y2 , x2], guess = False , output_format='csv', pages="10" )

  #Read Page 11

  if old:
    oldPdfToCsv(inp_file)
  else:
    out_file = 'out2.csv'
    tabula.convert_into( inp_file , out_file ,  stream=True  , output_format='csv', pages="11" )

  clnms1 = ['SN','DISTRICT/CORPORATION','TOTAL_CASES', 'NEW_CASES','TOTAL_DEATHS','NEW_DEATHS','RECOVERED']
  clnms2 = ['SN','DISTRICT/CORPORATION','TOTAL_CASES','TOTAL_DEATHS','NEW_DEATHS','RECOVERED']
  a = pd.read_csv("out1.csv")
  if len( a.columns ) == 7:
    a.columns = clnms1
  else:
    a.columns = clnms2
  b = pd.read_csv("out2.csv" , names=a.columns )

  merged = pd.concat([a,b])

  cols = merged.columns

  # merged.rename( columns = { 'S.\rN' : 'SN' , 'TOTAL\rCASES' : 'TOTAL_CASES' , 'NEW\rCASES': 'NEW_CASES', 'TOTAL\rDEATHS' : 'TOTAL_DEATHS', 'NEW\rDEATHS': 'NEW_DEATHS'}, inplace=True )
  merged = merged.replace({r'\r': ' '}, regex=True)
  

  out_file = 'outs/' + filename.split('.')[0] + '.csv'

  merged.to_csv(out_file , index=False)

  return out_file


def findAndUpdateLatest(old_date):
  resp = getReportTweets()
  dates = []
  get_fname = lambda x : '_'.join(str(x).split(" ")[0].split('-'))

  for d in resp.keys():
    if d > old_date:
      dates.append( d )

  dates.sort()

  if len(dates) < 1:
    print("No Updates")
    return { "status" : "No New Tweet" }
  
  upts = []

  for date in dates:
    fname = get_fname( date )
    downloadPdf( resp[ date ]['url'] , fname + '.pdf' )
    df_loc = pdfToCsv( fname + '.pdf' )
    data = getDicFromDfLoc( df_loc , date )
    upts.append( data )

  if len(upts) > 0:
    old_data_col.insert_many(upts)
    latest_data_col.delete_many({})
    latest_data_col.insert_one( upts[-1] )
    print("Update Successfull")
  
  return { "status" : "Updated the Database" }

  
def checkIfLatest():
  latest_data_col = covidapidb.get_collection('latest_data')
  data = latest_data_col.find_one()
  old_date = data['date']
  today = datetime.today()
  cur_date = datetime( today.year , today.month , today.day , 0 , 0)

  

  if cur_date > old_date:
    
    print("outdated" , "cur_date ", cur_date , "old_date" , old_date)
    resp = findAndUpdateLatest(old_date)
    return resp

  else:

    print("latest")
    return { "status": "latest"}




