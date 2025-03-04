from django.urls import path
from .views import AvatarUploadView, ProfileDetailAPIView, ProfileUpdateAPIView

urlpatterns = [
    path("user/my-profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),
    path("user/update/", ProfileUpdateAPIView.as_view(), name="profile-update"),
    path("user/avatar/", AvatarUploadView.as_view(), name="avatar-upload"),
]
