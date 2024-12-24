from django.contrib import admin
from .models import Stamp

@admin.register(Stamp)
class StampAdmin(admin.ModelAdmin):
    list_display = ("artist_name", "concert_name", "date", "created_at")
    search_fields = ("artist_name", "concert_name")
