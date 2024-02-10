from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Panggil default exception handler
    response = exception_handler(exc, context)

    if response is not None:
        # Ubah key 'detail' menjadi 'message' jika tersedia dalam response
        response.data['message'] = response.data.pop('detail', None)
        response.data['success'] = False

    return response
