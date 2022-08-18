from flask import Flask, jsonify, request, render_template
from google.cloud import bigquery, storage
from typing import Union
from datetime import datetime, timedelta
import logging
import json
  
app = Flask(__name__)



# Construct a BigQuery client object.
client = bigquery.Client()

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET_DEV = "ad-forecasting-nu-central" 
CLOUD_STORAGE_BUCKET_PROD = "ad-forecasting-nu-central-prod" 

#@app.route('/openFile')
def openFile():
    gcs = storage.Client()
    try:
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_PROD)
    except:
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_DEV)
    blob = bucket.get_blob('environment_variables.json')

    data = json.loads(blob.download_as_string())
    return data

env_variables = openFile()

# import env_variables here:

table_id = env_variables['GBQ_TABLE_ID'] #"ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

model_id = env_variables['GBQ_ML_MODEL']

sql_1 = """
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
    table_id
)

job_dev = client.query(sql_1)  # API request.
job_dev.result()  # Waits for the query to finish.

def get_days(start_date, end_date):
    d_string1 = start_date
    d_string2 = end_date

    date_time_obj1 = datetime.strptime(d_string1, '%Y-%m-%d')
    date_time_obj2 = datetime.strptime(d_string2, '%Y-%m-%d')

    delta = date_time_obj2-date_time_obj1

    delta_days = delta.days
    media_days = delta.days + 1

    return delta_days, media_days


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
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_PROD)
    except:
        bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET_DEV)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(uploaded_file.filename)

    blob.upload_from_string(
        uploaded_file.read(),
        content_type=uploaded_file.content_type
    )

    return blob.path

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
        q_start_date = request.args.get('start_date')
        q_end_date = request.args.get('end_date')
        q_client = request.args.get('client')
        q_sg = request.args.get('seasongroup')
        q_funnel = request.args.get('funnel')
        q_mt = request.args.get('mediatype')
        q_spend = request.args.get('spend')
        q_imp = request.args.get('impressions')

        q_delta_days, q_media_days = get_days(q_start_date, q_end_date)

        q_daily_imp = int(int(q_imp) / q_media_days)
        q_daily_spend = int(int(q_spend) / q_media_days)

        prediction = 0

        json_data = {"total_prediction": [], "dates":[],"daily_prediction":[]}

        loop_days = 0

        for day_ix in range(7):
            loop_days += 1
            pred_date = datetime.strptime(q_start_date, '%Y-%m-%d') + timedelta(days=day_ix)
            q_pred_date = pred_date.strftime('%Y-%m-%d')
            q_day_of_week = pred_date.isoweekday()
            q_week_of_date = pred_date.isocalendar().week
            q_qtr_of_date = (pred_date.month-1)//3+1
            q_yr_of_date = pred_date.year

            sql_pred = """
            SELECT * FROM ML.PREDICT(MODEL `{0}`, #`ad-forecasting-nu.d_ad_forecasting_nu.sample_model`, 
            (SELECT 
              CAST("{1}" AS DATE) AS date,
              {2} AS day_of_week,
              {3} AS week_of_date,
              {4} AS quarter_of_date, 
              {5} AS year_of_date, 
              {6} AS client,
              {7} AS seasongroup,
              {8} AS funnel,
              {9} AS mediatype, 
              {10} AS spend,
              {11} AS impressions
            )
            );
            """.format(
                model_id,
                q_pred_date,
                q_day_of_week,
                q_week_of_date,
                q_qtr_of_date,
                q_yr_of_date,
                q_client,
                q_sg,
                q_funnel,
                q_mt,
                q_daily_spend,
                q_daily_imp
            )

            predict_qry = client.query(sql_pred)  # API request.
            data = predict_qry.result()
            predict_df = predict_qry.to_dataframe()  # Waits for the query to finish.
            prediction += predict_df['predicted_total_revenue']
            
            json_data['dates'].append(q_pred_date)
            json_data['daily_prediction'].append(int(predict_df['predicted_total_revenue']))

        json_data['total_prediction'] = int(prediction)/loop_days*q_media_days  
        json_str = json.dumps(json_data, indent=4)
        return json_str

@app.route('/tasks/update_data', methods=['GET'])
def update_data():    
    client = bigquery.Client() 

    table_id_update = table_id #"ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

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
            bigquery.SchemaField("video_completions", "numeric"),
            bigquery.SchemaField("video_views", "integer"),
            bigquery.SchemaField("impressions", "integer"),
            bigquery.SchemaField("post_engagement", "integer"),
            bigquery.SchemaField("purchases", "integer"),
            bigquery.SchemaField("clicks", "integer"),
            bigquery.SchemaField("video_50_watched", "numeric")
        ],
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    try:
        uri = "gs://{0}/raw_marketing_data.csv".format(CLOUD_STORAGE_BUCKET_DEV)

        load_job = client.load_table_from_uri(
            uri, table_id_update, job_config=job_config
        )  # Make an API request.

        load_job.result()  # Waits for the job to complete.

        return "Success"
    except:
        uri = "gs://{0}/raw_marketing_data.csv".format(CLOUD_STORAGE_BUCKET_PROD)

        load_job = client.load_table_from_uri(
            uri, table_id_update, job_config=job_config
        )  # Make an API request.

        load_job.result()  # Waits for the job to complete.

        return "Success"

  
if __name__=='__main__':
	app.run(host="localhost", port=8080, debug=True)