from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
import os, json

app = FastAPI()

# Load GA4 client
try:
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
        creds_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        credentials = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
    else:
        client = None
except Exception as e:
    print("Error initializing GA4 client:", e)
    client = None


@app.get("/")
def root():
    return {"message": "GA4 MCP Server running on Vercel"}


@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Privacy Policy</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; max-width: 800px; }
            h1 { color: #333; }
            p { margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <h1>Privacy Policy</h1>
        <p>Your privacy is important to us. This app connects to the Google Analytics 4 (GA4) API in order to fetch and display analytics data that you request through the custom GPT.</p>

        <h2>Data Collection</h2>
        <p>We do not collect, store, or share any personal data. All data accessed comes directly from your connected Google Analytics property using credentials you provide via Google Cloud service account.</p>

        <h2>Data Usage</h2>
        <p>The data retrieved from GA4 is used solely to answer queries and provide reports inside the GPT interface. It is not stored or processed outside of your session.</p>

        <h2>Third-Party Access</h2>
        <p>We do not share your information with any third parties. Authentication is handled securely with Google’s official APIs.</p>

        <h2>Security</h2>
        <p>All requests between the GPT, this connector, and Google’s APIs are encrypted using HTTPS.</p>

        <h2>Contact</h2>
        <p>If you have questions about this Privacy Policy, please contact the developer of this connector.</p>
    </body>
    </html>
    """


@app.post("/run_report")
async def run_report(request: Request):
    if not client:
        return {"error": "GA4 client not initialized"}

    try:
        body = await request.json()
        property_id = body.get("propertyId")
        start_date = body.get("startDate", "7daysAgo")
        end_date = body.get("endDate", "today")
        metrics = body.get("metrics", ["sessions"])
        dimensions = body.get("dimensions", ["date"])

        req = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            metrics=[Metric(name=m) for m in metrics],
            dimensions=[Dimension(name=d) for d in dimensions],
        )
        response = client.run_report(req)

        rows = []
        for row in response.rows:
            rows.append(
                [v.value for v in row.dimension_values] +
                [v.value for v in row.metric_values]
            )

        return {
            "header": [d.name for d in req.dimensions] + [m.name for m in req.metrics],
            "rows": rows
        }
    except Exception as e:
        print("Error in run_report:", e)
        return {"error": str(e)}
