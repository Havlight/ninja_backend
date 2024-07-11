from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import File
from ninja.files import UploadedFile
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ultralytics import YOLO
from ninja_backend.apps.yolo.models import Image
import os
import cv2

User = get_user_model()

@api_controller("/yolo", tags=["yolo"], auth=JWTAuth())
class ImageController:
    @route.post("/upload")
    def upload_image(self, request, file: UploadedFile = File(...)):
        user = get_object_or_404(User, id=request.user.id)
        # Save the uploaded file to the desired location
        image_path = os.path.join('media', 'images', file.name)
        with open(image_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Create an Image instance in the database
        image = Image.objects.create(user=user, image=image_path)

        # Load the YOLO model and perform prediction
        model = YOLO('yolov8s.pt')
        results = model(image_path)

        # Save the prediction result image
        output_dir = os.path.join('media', 'yolo_out')
        os.makedirs(output_dir, exist_ok=True)
        output_image_path = os.path.join(output_dir, f"pred_{file.name}")
        results[0].save(output_image_path)

        return {
            "filename": file.name,
            "url": f"/media/images/{file.name}",
            "prediction_url": f"/media/yolo_out/pred_{file.name}",
            "user_id": request.user.id
        }
