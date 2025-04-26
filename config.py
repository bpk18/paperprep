import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload size
    ALLOWED_EXTENSIONS = {
        'doc', 'docx', 'odt', 'rtf', 'txt', 'pdf',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff', 'svg',
        'mp3', 'wav', 'ogg', 'flac', 'aac', 'wma',
        'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm',
        'zip', 'rar', '7z', 'tar', 'gz'
    }