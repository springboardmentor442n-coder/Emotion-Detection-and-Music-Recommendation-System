"""
MoodMate URL Configuration.

API endpoints:
    POST /api/predict/image/  →  ImagePredictView
    POST /api/predict/text/   →  TextPredictView
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/predict/image/', views.ImagePredictView.as_view(), name='predict-image'),
    path('api/predict/text/', views.TextPredictView.as_view(), name='predict-text'),
]
