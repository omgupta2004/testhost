from django.db import models
import os

class VideoUpload(models.Model):
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Video {self.id} - {self.uploaded_at}"

class ComicPanel(models.Model):
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE, related_name='panels')
    image_file = models.ImageField(upload_to='comics/')
    panel_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['panel_number']

    def __str__(self):
        return f"Panel {self.panel_number} for Video {self.video.id}"
