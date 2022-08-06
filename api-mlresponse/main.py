from flask import Flask, jsonify, request, render_template
from google.cloud import bigquery, storage
from typing import Union
import logging
  
app = Flask(__name__)

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO(developer): Set table_id to the ID of the table to create.
table_id_dev = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

table_id_prod = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_prod"

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET_DEV = "ad-forecasting-nu-central" 
CLOUD_STORAGE_BUCKET_PROD = "ad-forecasting-nu-central-prod" 

sql_dev = """
CREATE TABLE IF NOT EXISTS `{0}` 
(
    date string,
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
    date string,
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

@app.route('/file_uploaded', methods=['POST'])
def file_uploaded() -> str:
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    try:
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_DEV)
    except:
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_PROD)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    return blob.path

@app.route('/openFile')
def openFile():
    client = storage.Client()
    try:
        bucket = client.get_bucket({0}).format(CLOUD_STORAGE_BUCKET_PROD)
    try:
        bucket = client.get_bucket({0}).format(CLOUD_STORAGE_BUCKET_DEV)
    blob = bucket.get_blob('data/movie_lines.txt')
    your_file_contents = blob.download_as_string()
    return your_file_contents


@app.errorhandler(500)
def server_error(e: Union[Exception, int]) -> str:
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500
  
@app.route('/', methods=['GET'])
def helloworld():
    if(request.method == 'GET'):
        q_date = request.args.get('date')
        q_client = request.args.get('client')
        q_sg = request.args.get('seasongroup')
        q_funnel = request.args.get('funnel')
        q_mt = request.args.get('mediatype')
        q_spend = request.args.get('spend')
        q_sv = request.args.get('site_visits')
        q_imp = request.args.get('impressions')

        sql_dev = """
        SELECT * FROM ML.PREDICT(MODEL `ad-forecasting-nu.d_ad_forecasting_nu.sample_model`, 
        (SELECT 
          CAST("{0}" AS date) AS date,
          {1} AS client,
          {2} AS seasongroup,
          {3} AS funnel,
          {4} AS mediatype, 
          {5} AS spend,
          {6} AS site_visits,
          {7} AS impressions
        )
        );
        """.format(
            q_date,
            q_client,
            q_sg,
            q_funnel,
            q_mt,
            q_spend,
            q_sv,
            q_imp
        )


        predict_dev = client.query(sql_dev)  # API request.
        data = predict_dev.result()
        predict_df = predict_dev.to_dataframe()  # Waits for the query to finish.
        predict_json = predict_df.to_json()

        return predict_json

@app.route('/tasks/update_data', methods=['GET'])
def update_data():    
    client = bigquery.Client()

    table_id_dev = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("date", "string"),
            bigquery.SchemaField("clientid", "integer"),
            bigquery.SchemaField("clientname", "string"),
            bigquery.SchemaField("mediatype", "string"),
            bigquery.SchemaField("funnel", "string"),
            bigquery.SchemaField("seasongroup", "string"),
            bigquery.SchemaField("spend", "numeric"),
            bigquery.SchemaField("total_revenue", "numeric"),
            bigquery.SchemaField("site_visits", "integer"),
            bigquery.SchemaField("video_completions", "integer"),
            bigquery.SchemaField("video_views", "integer"),
            bigquery.SchemaField("impressions", "integer"),
            bigquery.SchemaField("post_engagement", "integer"),
            bigquery.SchemaField("purchases", "integer"),
            bigquery.SchemaField("clicks", "integer"),
            bigquery.SchemaField("video_50_watched", "integer")
        ],
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    uri = "gs://ad-forecasting-nu-central/raw_marketing_data.csv"

    load_job = client.load_table_from_uri(
        uri, table_id_dev, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.

    return "Success"

  
if __name__=='__main__':
	app.run(host="localhost", port=8080, debug=True)