# 🚀 LinkedIn Post Scraper API

This is a FastAPI-based REST API to scrape LinkedIn posts based on a search keyword using a valid LinkedIn session cookie (`li_at`). The API supports optional limiting of post count and provides name, profile URL, and post content.

---

## ⚙️ Setup Instructions

### 1. Clone Repository & Navigate to Folder
```bash
git clone https://github.com/Muskanrath2234/linkedin_scraper.git
cd linkedin-scraper


2. Install Requirements
pip install -r requirements.txt


3. Run the API Locally
uvicorn main:app --reload
Local API will be available at:
http://127.0.0.1:8000

Swagger documentation:
http://127.0.0.1:8000/docs


🧪 API Endpoint
POST /scrape-linkedin
Description: Scrapes LinkedIn posts using search keyword and session cookie.

📤 Request Body (JSON)
json

{
  "keyword": "data scientist",
  "sessioncookie": "YOUR_LI_AT_COOKIE",
  "max_posts": 5
}

keyword (string): The search term you want to use.
sessioncookie (string): Your valid LinkedIn li_at cookie.
max_posts (integer, optional): Number of posts to return (default: all found).

✅ Example Successful Response
json
Copy
Edit
{
  "status": "success",
  "keyword": "data scientist",
  "results": [
    {
      "post_number": 1,
      "name": "John Doe",
      "profile_url": "https://www.linkedin.com/in/johndoe",
      "content": "Excited to share my new project in data science..."
    },
    ...
  ]
}
🧰 How to Use in Postman or No-Code Tools
Open Postman (or similar tool like Hoppscotch/NocodeAPI).

Set method to POST.

Use URL: http://127.0.0.1:8000/scrape-linkedin

Set Header:
Content-Type: application/json

In Body (Raw - JSON), enter:

json
{
  "keyword": "machine learning hiring",
  "sessioncookie": "YOUR_LI_AT_COOKIE",
  "max_posts": 3
}
Click Send and view the response.

🌍 Deploy on Public URL using Ngrok
Install ngrok if not already installed.
bash
ngrok http 8000
Ngrok will provide a public URL like:

https://1234abcd.ngrok.io
Use this public URL in Postman or frontend instead of localhost:

https://1234abcd.ngrok.io/scrape-linkedin
⚠️ Important Notes
Use your own valid li_at session cookie from LinkedIn.

Do not overuse or abuse the API; scraping violates LinkedIn’s terms.

Make sure you install Chrome and allow it in headless mode.

The scraper uses Selenium and BeautifulSoup to extract post details.
