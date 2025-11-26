from django.urls import path
from . import views

urlpatterns = [
    path("send/", views.send_otp_view, name="otp_send"),
    path("verify/", views.verify_otp_view, name="otp_verify"),
]
