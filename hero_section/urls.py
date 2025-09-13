
# urls.py (in your app)
from django.urls import path
from . import views

urlpatterns = [
    path('hero-section/', views.hero_section_api, name='hero-section-api'),
    path('feature-cards/', views.feature_cards_api, name='feature-cards-api'),
]
