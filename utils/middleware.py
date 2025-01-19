from django.http import HttpResponse
from django.conf import settings
import magic

class ValidateFileUploadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.FILES:
            for file in request.FILES.values():
                # Check file size
                if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                    return HttpResponse(
                        '{"error": "File size exceeds maximum limit"}',
                        status=400,
                        content_type='application/json'
                    )

                # Check file type using python-magic
                mime = magic.from_buffer(file.read(1024), mime=True)
                file.seek(0)  # Reset file pointer
                
                allowed_types = [
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                ]
                
                if mime not in allowed_types:
                    return HttpResponse(
                        '{"error": "Invalid file type. Only PDF and Word documents are allowed"}',
                        status=400,
                        content_type='application/json'
                    )

        response = self.get_response(request)
        return response 