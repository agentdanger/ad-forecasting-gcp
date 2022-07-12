from flask import Flask, jsonify, request, render_template
from google.cloud import bigquery
  
app = Flask(__name__)

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO(developer): Set table_id to the ID of the table to create.
table_id_dev = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

table_id_prod = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_prod"

sql_dev = """
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
    table_id_dev
)

sql_prod = """
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
    table_id_prod
)

job_dev = client.query(sql_dev)  # API request.
job_dev.result()  # Waits for the query to finish.

job_prod = client.query(sql_prod)  # API request.
job_prod.result()  # Waits for the query to finish.


@app.route('/upload')
def index():
     # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')
  
@app.route('/', methods=['GET'])
def helloworld():
    if(request.method == 'GET'):
        data = {"data": "Hello World"}
        return jsonify(data)  
  
if __name__=='__main__':
	app.run(host="localhost", port=8080, debug=True)