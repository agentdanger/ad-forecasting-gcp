from flask import Flask, jsonify, request
from google.cloud import bigquery
  
app = Flask(__name__)

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO(developer): Set table_id to the ID of the table to create.
table_id = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

sql = """
CREATE TABLE IF NOT EXISTS `{0}` 
(
    date date,
    clientid integer,
    clientname string,
    mediatype string,
    funnel string,
    seasongroup string,
    spend numeric,
    total_revenue numeric,
    site_visits integer,
    video_completions integer,
    video_views integer,
    impressions integer,
    post_engagement integer,
    purchases integer,
    clicks integer,
    video_50_watched integer,
);
""".format(
    table_id
)

job = client.query(sql)  # API request.
job.result()  # Waits for the query to finish.
  
  
@app.route('/', methods=['GET'])
def helloworld():
    if(request.method == 'GET'):
        data = {"data": "Hello World"}
        return jsonify(data)  
  
if __name__=='__main__':
	app.run(host="localhost", port=8080, debug=True)