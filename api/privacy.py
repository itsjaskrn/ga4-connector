from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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
