from fastapi import FastAPI, Request
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
import os, json

app = FastAPI()

# Load credentials either from Vercel env var OR from local file
credentials = None
client = None

if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON"):
    # Vercel / environment variable setup
    creds_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
elif os.path.exists("credentials.json"):
    # Local testing setup (fallback to file)
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )

if credentials:
    client = BetaAnalyticsDataClient(credentials=credentials)

@app.get("/")
def root():
    return {"message": "GA4 MCP Server running"}

@app.post("/run_report")
async def run_report(request: Request):
    if not client:
        return {"error": "GA4 client not initialized. Did you set up credentials?"}

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
        rows.append([v.value for v in row.dimension_values] +
                    [v.value for v in row.metric_values])

    return {
        "header": [d.name for d in req.dimensions] + [m.name for m in req.metrics],
        "rows": rows
    }
