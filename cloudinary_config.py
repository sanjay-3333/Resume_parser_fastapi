import cloudinary
import cloudinary.uploader

# Replace with your actual credentials from https://cloudinary.com/console
cloudinary.config(
    cloud_name="your_cloud_name",
    api_key="your_api_key",
    api_secret="your_api_secret"
)
