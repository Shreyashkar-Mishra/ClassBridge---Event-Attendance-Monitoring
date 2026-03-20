# 📺 ClassBridge YouTube API Integration Guide

Currently, ClassBridge uses a clever but simple way to suggest videos: it generates a link to manual YouTube search results. If you want an actual **Feed** of videos directly inside your dashboard, you need the **YouTube Data API v3**.

---

### 🛠️ Step 1: Getting the API Key
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project called "ClassBridge".
3. Search for **"YouTube Data API v3"** and click **Enable**.
4. Go to **Credentials** -> **Create Credentials** -> **API Key**.
5. **CRITICAL:** Copy this key into your `settings.py` (e.g., `YOUTUBE_API_KEY = 'YOUR_KEY_HERE'`).

---

### 🛠️ Step 2: Installing requirements
You need a library to talk to Google easily:
```bash
pip install google-api-python-client
```

---

### 🛠️ Step 3: Upgrading the `ClassLog` Model
Update your `get_ai_video_links` method in `models.py` to actually fetch data.

```python
import googleapiclient.discovery
from django.conf import settings

def get_real_youtube_feed(self, topic):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=settings.YOUTUBE_API_KEY
    )

    request = youtube.search().list(
        q=f"{self.subject} {topic} tutorial",
        part="snippet",
        maxResults=3, # Show top 3 videos
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response['items']:
        videos.append({
            'title': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'video_id': item['id']['videoId'],
            'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })
    return videos
```

---

### 🛠️ Step 4: Displaying in the Dashboard
Instead of a simple link, you can now use the `thumbnail` and `title` to create a beautiful "Video Gallery" in your `dashboard_student.html`.

```html
{% for video in videos %}
  <div class="video-card">
    <img src="{{ video.thumbnail }}" alt="{{ video.title }}">
    <p>{{ video.title }}</p>
    <a href="{{ video.url }}" target="_blank">Watch Now</a>
  </div>
{% endfor %}
```

---

### ⚠️ Important Considerations:
1. **Quotas**: Google gives you 10,000 units per day for free. A "search" costs about 100 units. If you have many students, you'll hit the limit quickly!
2. **Caching**: To save your quota, you should **Cache** the results. Don't call the API every time a student refreshes their page. Store the results in the database or use Django's Cache framework.
3. **Environment Variables**: Never hardcode your API key! Use a `.env` file to keep it secret.

---

> ✏️ *This upgrade will make ClassBridge feel much more professional and automated.*
