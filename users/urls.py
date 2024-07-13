from django.urls import path

from users import views

urlpatterns = [
    path('get_user/', views.get_user),
    path('update_profile/', views.update_profile),
]
