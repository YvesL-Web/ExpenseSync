from typing import List

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import Http404

from rest_framework import filters, generics
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from config.utils.renderers import GenericJSONRenderer
from .serializers import AvatarUploadSerializer, ProfileSerializer, UpdateProfileSerializer
from .tasks import upload_avatar_to_cloudinary
from .models import Profile

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 100



class ProfileDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    renderer_classes = [GenericJSONRenderer]
    object_label = "profile"

    # def get_queryset(self) -> QuerySet:
    #     return Profile.objects.select_related("user").all()
    
    def get_object(self) -> Profile:
        try:
            return Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise Http404("Profile Not Found")
        

class ProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UpdateProfileSerializer
    renderer_classes = [GenericJSONRenderer]
    object_label = "profile"
    
    def get_queryset(self):
        return Profile.objects.none()
    
    def get_object(self) -> Profile:
        profile, _ = Profile.objects.get_or_create(user = self.request.user)
        return  profile
    
    def perform_update(self, serializer: UpdateProfileSerializer) -> Profile:
        user_data = serializer.validated_data.pop("user",{})
        profile = serializer.save()
        User.objects.filter(id=self.request.user.id).update(**user_data)
        return profile
    

class AvatarUploadView(APIView):

    def patch(self, request, *args, **kwargs):
        return self.upload_avatar(request, *args, **kwargs)
    
    def upload_avatar(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = AvatarUploadSerializer(profile, data=request.data)

        if serializer.is_valid():
            image = serializer.validated_data["avatar"]
            image_content = image.read()
            upload_avatar_to_cloudinary.delay(str(profile.id), image_content)

            return Response(
                {"message":"Avatar upload started."}, status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
