import cloudinary.uploader
import qrcode
import io
from src.conf.cloudinary import configure_cloudinary, generate_random_string
from fastapi import HTTPException, status

async def generate_qr_and_upload_to_cloudinary(url: str, picture: dict = None) -> str:
    
    configure_cloudinary()
    random_string = generate_random_string()

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_bytes = io.BytesIO()
        qr_img.save(qr_bytes, format='JPEG')
        qr_bytes.seek(0)

        if picture:
            picture_folder = picture['folder']
            picture_public_id = picture['public_id']
            picture_version = picture['version']
            picture_name = picture_public_id.replace(picture_folder + "/", "")

            qr_upload = cloudinary.uploader.upload(qr_bytes, folder='qr_code', public_id=picture_name, version=picture_version, overwrite=True)
            qr_public_id = qr_upload['public_id']

            qr_url = cloudinary.CloudinaryImage(qr_public_id).build_url(version=picture_version)
        else:
            picture_name = generate_random_string()
            qr_upload = cloudinary.uploader.upload(qr_bytes, folder='profile_qr_code', public_id=picture_name, overwrite=True)
            qr_public_id = qr_upload['public_id']
            qr_url = cloudinary.CloudinaryImage(qr_public_id).build_url(version=qr_upload['version'])
            
        return qr_url

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))