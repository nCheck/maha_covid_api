# Maha-Covid-Api
#

Maha-Covid-Api is API for Maharashtra Corona Cases with district wise data. This data is not widely available in other APIs or Website. This data is upload in PDF report format by twitter account of [ Medical Education & Drugs Department, Maharashtra ](https://twitter.com/Maha_MEDD) ( [sample report]( https://drive.google.com/file/d/1PjkafyLnCxLh5ul-LSeHckhqfMXzOf40/view ) ) 


## Data Extraction :
  - Track daily tweets of @Maha_MEDD account with key words "A daily comprehensive report prepared by MEDD, Maharashtra showing #COVIDー19 situation in the state" 
  - Extract the Google Drive url of pdf from tweet and download the pdf on server
  - Extract the Report Table from Pdf using [Tabula]( https://github.com/chezou/tabula-py )
  - Apply Data Cleaning to get useful data
  - Update the database
  - Data is automatically using AWS Lambda & AWS Cloudwatch Events



### Installation

Maha-Covid-Api requires Python 3.X+ to run.
Create a virtual env using Conda or virtualenv install the dependencies and start the server.

```sh
$ cd maha_covid_api
$ pip install requirements.txt
$ python app.py
```



## API


| PATH | METHOD | DESCRIPTION |
| ------ | ------ | ------ |
| /latest | GET | Get the latests statistics of all districts/muncipals |
| /ids | GET | Get ids of all districts/muncipals to use for history API |
| /all | GET | Get all information from database
| /history/:id | GET | Get past 14 days information of particular districts/muncipals  |


### Link to API: https://maha-covid-api.herokuapp.com/
