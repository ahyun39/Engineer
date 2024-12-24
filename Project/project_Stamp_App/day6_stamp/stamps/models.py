from django.db import models

class Stamp(models.Model):
    concert_name = models.CharField(max_length=200)  # 공연명
    artist_name = models.CharField(max_length=200)  # 가수명
    date = models.DateField()  # 공연 날짜
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

    def __str__(self):
        return f"{self.artist_name} - {self.concert_name} ({self.date})"
