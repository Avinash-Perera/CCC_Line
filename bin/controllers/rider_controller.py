import base64
import os
import uuid
from bin.response.response_model import ResponseModel,ErrorResponseModel
from bin.services.db_services.rider_service import  create_new_rider,all_riders

class RiderManager():
    def rider_registration(self,request):
        try:
            uuid_digit = str(uuid.uuid4().int)[:4]  # Get first 4 digits
            print(uuid_digit)

            print('type of image -', type(request.rider_img))
            # Validate and parse the base64 data
            if not request.rider_img or not isinstance(request.rider_img, str):
                raise ValueError("Invalid or missing 'rider_img' field in the request.")

            if "base64," not in request.rider_img:
                raise ValueError("The 'rider_img' field is not a valid base64-encoded image.")

            base64_data = request.rider_img.split(",")[1]  # Extract base64 image data after the comma

            image_data = base64.b64decode(base64_data)  # Decode the base64 data

            file_dir = os.path.join(os.getcwd(), 'public', 'images', 'avatars')  # Absolute path to the images directory
            # Ensure the directory exists
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, exist_ok=True)  # Create the directory if it doesn't exist

            img_name = f"{uuid_digit}.jpg"  # Construct the image filename
            file_path = os.path.join(file_dir, img_name)  # Full file path

            with open(file_path, "wb") as f:
                f.write(image_data)

            print(f"Image successfully saved at: {file_path}")
            create_new_rider(request,img_name)
            return ResponseModel(request,"Succesfully created new donation")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)


    def get_all_riders(self):
        try:
            rider_list = all_riders()

            return ResponseModel(rider_list,'All Rider List')

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ErrorResponseModel(str(e), 400)



riderManager = RiderManager()