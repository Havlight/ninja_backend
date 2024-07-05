from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import File
from ninja.files import UploadedFile
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

User = get_user_model()
from ninja_backend.apps.yolo.models import Image


@api_controller("/yolo", tags=["yolo"], auth=JWTAuth())
class ImageController:
    @route.post("/upload")
    def upload_image(self, request, file: UploadedFile = File(...)):
        user = get_object_or_404(User, id=request.user.id)
        image = Image.objects.create(user=user, image=file)
        return {"filename": file.name, "url": f"/media/images/{file.name}", "user id": request.user.id}
