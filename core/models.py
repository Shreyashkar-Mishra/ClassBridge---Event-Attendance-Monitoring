from django.db import models
from django.contrib.auth.models import AbstractUser
import urllib.parse
from django.conf import settings
import googleapiclient.discovery

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student','Student'),
        ('faculty','Faculty'),
        ('coordinator','Coordinator')
    )

    user_type = models.CharField(max_length=20,choices=USER_TYPE_CHOICES,default='student')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Faculty(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,
    related_name='faculty_profile')
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.department}"


class Student(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,
    related_name='student_profile')
    roll_number = models.CharField(max_length=20,unique=True)
    batch = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.roll_number})"

class Coordinator(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE,
    related_name='coordinator_profile')
    assigned_batch = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    created_by = models.ForeignKey(Coordinator, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class ClassLog(models.Model):
    date = models.DateField()
    subject = models.CharField(max_length=100)
    topics_covered = models.TextField()
    assignments = models.TextField(blank=True,null=True)
    logged_by = models.ForeignKey(Faculty,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject} - {self.date}"
    
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

    def get_ai_video_feed(self):
        """Combines multiple topics into a single list of video objects from the API."""
        topics = [t.strip() for t in self.topics_covered.split(',')]
        if len(topics) == 1:
            topics = [t.strip() for t in self.topics_covered.split('\n') if t.strip()]

        all_videos = []
        # To avoid hitting quota too hard, we only take the first 2 topics
        for topic in topics[:2]:
            if len(topic) > 3:
                try:
                    all_videos.extend(self.get_real_youtube_feed(topic))
                except Exception:
                    # Fallback to empty if API fails or quota exceeded
                    continue
        return all_videos

                
class Absence(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField(blank=True,null=True)
    is_excused = models.BooleanField(default=False)

    def __str__(self):
        return f"Absence: {self.student.user.first_name} {self.student.user.last_name} on {self.date}"
    
    

class EventParticipation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This prevents a student from joining the same event twice!
        unique_together = ('student', 'event')

    def __str__(self):
        return f"{self.student.user.first_name} -> {self.event.title}"


