from flask import Flask, jsonify, request, render_template
from google.cloud import bigquery, storage
  
app = Flask(__name__)

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO(developer): Set table_id to the ID of the table to create.
table_id_dev = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_dev"

table_id_prod = "ad-forecasting-nu.d_ad_forecasting_nu.t_ad_forecasting_data_prod"

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = "ad-forecasting-nu.appspot.com"

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

@app.route('/file_uploaded', methods=['POST'])
def file_uploaded() -> str:
    """Process the uploaded file and upload it to Google Cloud Storage."""
    uploaded_file = request.files.get('file')

    if not uploaded_file:
        return 'No file uploaded.', 400

    # Create a Cloud Storage client.
    gcs = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

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
        data = {"data": "Hello World"}
        return jsonify(data)  
  
if __name__=='__main__':
	app.run(host="localhost", port=8080, debug=True)