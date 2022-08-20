# Digital Ad Forecasting on Google Cloud Platform
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/agentdanger/ad-forecasting-gcp/tree/main.svg?style=svg&circle-token=88a4a43346f2808df6c5f1508b8b07a7174ff7dd)](https://dl.circleci.com/status-badge/redirect/gh/agentdanger/ad-forecasting-gcp/tree/main)

## Application Overview
This application is a Python Flask API that leverages machine learning and the Google Cloud Platform to forecast revenue attributed to an upcoming media plan for a select clients of an advertising agency. These forecasts are useful to set benchmarks for upcoming media plans so the media planner can set expectations of performance with clients and assist in optimizations.

## Using the API
To use the API, an analyst can send a GET request to the applications along with a series of query strings.  Based on the inputs in the query strings, the forecasting algorithm will provide an appropriate total revenue you can expect over the life of the campaign as well as a daily forcast for the first 7 days of the media activation.

Base URL:  https://ad-forecasting-nu-prod.uc.r.appspot.com/

### Interacting with the API:

All communication with the API is done through a GET request via https at the base URL above.  Responses will be communicated in JSON only when the appropriate fields are communicated <b>correctly</b> and <b>completely</b>.  

### Fields must be set correctly and completely.

You must include as part of a GET request the following fields set as query strings along with the base URL. The fields that the API takes are listed here:

- start_date:  (YYYY-MM-DD) the first day of the campaign to be forecasted.  Must be entered YYYY-MM-DD with no quotes.
- end_date: (YYYY-MM-DD) the last day of the campaign to be forecasted.  Must be entered YYYY-MM-DD with no quotes.
- client:  (int) the client id representing the client associated with the campaign to be forecasted.
- seasongroup: <i>str</i> (e.g. "haunt") the season associated with the campaign to be forecasted.
    seasongroup can be one of the following:
    - "conversion"
- funnel:  <i>str</i> (e.g. "conversion") the funnel associated with the campaign to be forecasted.  Only "conversion" is relevant at this time.
    funnel can be one of the following:
    - "Full Year"
    - "Group Sales"
    - "Haunt"
    - "Resorts"
    - "Season Pass Experience"
    - "Tourism"
- mediatype: <i>str</i> (e.g. "Facebook") the media associated with the campaign to be forecasted.
    Media types can only be one of the following:
    - "Audio"
    - "Display_Desck"
    - "Display_Direct"
    - "Facebook"
    - "FBIG"
    - "Instagram"
    - "Native_Desck"
    - "Paid Search: Brand Keywords"
    - "Paid Social Other"
    - "Video_FEP"
    - "Video_Preroll_Desck"
    - "Video_Preroll_Direct"
- spend <i>int</i> the amount of planned spend associated with the campaign to be forecasted.  Note:  This should be the total spend for the length of the campaign.
- impressions <i>int</i> the amount of planned impressions associated with the campaign to be forecasted.  This should be the total number of planned impressions for the length of the campaign.

### Example API Get Request:

https://ad-forecasting-nu-prod.uc.r.appspot.com/?start_date=2022-10-09&end_date=2022-10-23&client=2&seasongroup=%22haunt%22&funnel=%22conversion%22&mediatype=%22Facebook%22&spend=1500&impressions=42000

## API Response

With a correclty formatted GET request, you will receive a JSON response with the following format:

```
{ 
	"total_prediction": 81582.85714285714, 
	"dates": [ "2022-10-09", "2022-10-10", "2022-10-11", "2022-10-12", "2022-10-13", "2022-10-14", "2022-10-15" ], 
	"daily_prediction": [ 6948, 4835, 4835, 4835, 4835, 4835, 6948 ] 
}
```
- total_prediction:  <i>numeric</i> This is the total forecasted revenue for the length of the campaign.
- dates: <i>str</i> This is a list of the first seven days associated with the campaign.
- daily_prediction: <i>int</i> This is a list of the daily forecasted revenue associated with first seven days of the campaign.

## Using the CSV Uploader

https://ad-forecasting-nu-prod.uc.r.appspot.com/upload

The forecasting application does include the ability to update the data that the model will train off of.  At this time, the CSV uploader is disconnected from the ML algorithm to ensure the API functionality.  If an update to the model is requested, we can turn this service back on.  When turned on, the CSV uploader will check for a CSV file and store that in Google Cloud Storage to be processed by the model using a cron job set for 24 hour refreshes.

