from uuid import UUID
from celery import shared_task
from .models import Profile
import cloudinary.uploader 

@shared_task(name="upload_avatar_to_cloudinary")  # main purpose is to turn regular python function into celery task --- the decorator @shared_task
def upload_avatar_to_cloudinary(profile_id: UUID, image_content: bytes) -> None:
    profile = Profile.objects.get(id=profile_id)
    response = cloudinary.uploader.upload(image_content)
    profile.avatar = response["url"]
    profile.save()
