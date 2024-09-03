from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import File
from ninja.files import UploadedFile
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ultralytics import YOLO
from ninja_backend.apps.yolo.models import Image
import os
import datetime
import io

date = datetime.datetime.now().date()
time = datetime.datetime.now().time()

from PIL import Image as PILImage
import numpy as np

User = get_user_model()

@api_controller("/yolo", tags=["yolo"], auth=JWTAuth())
class ImageController:
    @route.post("/upload")
    def upload_image(self, request, file: UploadedFile = File(...)):
        user = get_object_or_404(User, id=request.user.id)

        # 直接從 UploadedFile 物件中讀取圖像並轉換為 numpy 數組
        image_stream = io.BytesIO(file.read())
        image = PILImage.open(image_stream)
        image_array = np.array(image)

        # 加載 YOLO 模型並進行預測
        model = YOLO('yolov8s.pt')
        results = model(image_array)

        # 提取檢測到的物件數量及其類別名稱
        detected_objects = results[0].names
        num_detected_objects = len(results[0].boxes)
        class_names = [model.names[int(box.cls)] for box in results[0].boxes]

        return {
            "filename": file.name,
            "user_id": request.user.id,
            "num_detected_objects": num_detected_objects,
            "class_names": class_names
        }

# @api_controller("/yolo", tags=["yolo"], auth=JWTAuth())
# class ImageController:
#     @route.post("/upload")
#     def upload_image(self, request, file: UploadedFile = File(...)):
#         user = get_object_or_404(User, id=request.user.id)
#         # Save the uploaded file to the desired location
#         image_path = os.path.join('media', 'images', f'{request.user.id}', f'{date}', f'{time.strftime("%H-%M-%S")}',
#                                   file.name)
#         os.makedirs(os.path.dirname(image_path), exist_ok=True)
#
#         with open(image_path, 'wb+') as destination:
#             for chunk in file.chunks():
#                 destination.write(chunk)
#
#         # Create an Image instance in the database
#         image = Image.objects.create(user=user, image=image_path)
#
#         # Load the YOLO model and perform prediction
#         model = YOLO('yolov8s.pt')
#         results = model(image_path)
#
#         # Extract the number of detected objects and their class names
#         detected_objects = results[0].names
#         num_detected_objects = len(results[0].boxes)
#         class_names = [model.names[int(box.cls)] for box in results[0].boxes]
#
#         # Save the prediction result image
#         output_dir = os.path.join('media', 'yolo_out', f'{request.user.id}', f'{date}', f'{time.strftime("%H-%M-%S")}',
#                                   f"pred_{file.name}")
#         os.makedirs(os.path.dirname(output_dir), exist_ok=True)
#
#         results[0].save(output_dir)
#
#         return {
#             "filename": file.name,
#             "url": f"/media/images/{file.name}",
#             "prediction_url": f"/media/yolo_out/pred_{file.name}",
#             "user_id": request.user.id,
#             "num_detected_objects": num_detected_objects,
#             "class_names": class_names
#         }