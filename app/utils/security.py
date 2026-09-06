import os
import uuid
from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user
from werkzeug.utils import secure_filename

# Allowed MIME types matching allowed extensions
ALLOWED_MIME_TYPES = {
    'pdf': {'application/pdf'},
    'png': {'image/png'},
    'jpg': {'image/jpeg', 'image/pjpeg'},
    'jpeg': {'image/jpeg', 'image/pjpeg'}
}

def role_required(*allowed_roles):
    """
    Decorator for enforcing role-based access control.
    Supports single or multiple allowed roles:
    @role_required('admin')
    @role_required('pharmacy', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # Flatten role arguments if passed as list or tuple
            roles = []
            for r in allowed_roles:
                if isinstance(r, (list, tuple)):
                    roles.extend(r)
                else:
                    roles.append(r)

            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_file_upload(file_storage, allowed_extensions=None, max_size=None):
    """
    Validates uploaded file for:
    1. Presence
    2. Extension
    3. Content size
    4. MIME type check
    Returns (is_valid: bool, error_message: str or None, ext: str or None)
    """
    if not file_storage or file_storage.filename == '':
        return False, "No file selected.", None

    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg'})

    if max_size is None:
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)

    # Validate extension
    filename = secure_filename(file_storage.filename)
    if '.' not in filename:
        return False, "File must have a valid extension.", None

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return False, f"Unsupported file type (.{ext}). Allowed types: {', '.join(allowed_extensions)}", None

    # Check file size (seek to end and back)
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)

    if size > max_size:
        return False, f"File size ({size / (1024*1024):.1f}MB) exceeds the maximum allowed limit of {max_size / (1024*1024):.1f}MB.", None

    if size == 0:
        return False, "Uploaded file is empty.", None

    # Verify mime type matches extension
    mimetype = file_storage.mimetype or file_storage.content_type
    expected_mimes = ALLOWED_MIME_TYPES.get(ext, set())
    
    # Basic header magic check
    header = file_storage.read(16)
    file_storage.seek(0)
    
    if ext == 'pdf' and not header.startswith(b'%PDF'):
        return False, "File content is not a valid PDF document.", None
    elif ext == 'png' and not header.startswith(b'\x89PNG\r\n\x1a\n'):
        return False, "File content is not a valid PNG image.", None
    elif ext in ('jpg', 'jpeg') and not header.startswith(b'\xff\xd8'):
        return False, "File content is not a valid JPEG image.", None

    return True, None, ext


def save_secure_upload(file_storage, target_directory, prefix='doc'):
    """
    Saves an uploaded file with a randomized UUID filename outside static paths.
    Returns: (saved_relative_path, original_filename, mime_type, file_size)
    """
    os.makedirs(target_directory, exist_ok=True)
    
    original_filename = secure_filename(file_storage.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'bin'
    
    unique_filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    destination_path = os.path.join(target_directory, unique_filename)
    
    file_storage.save(destination_path)
    file_size = os.path.getsize(destination_path)
    mime_type = file_storage.mimetype or 'application/octet-stream'

    return unique_filename, original_filename, mime_type, file_size
