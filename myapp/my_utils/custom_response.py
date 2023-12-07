from rest_framework.response import Response
from rest_framework import status


class CustomResponse:

    def list(message, data):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    def retrieve(message, data):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )

    def created(message, data, headers=None):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
        
    def updated(message, data):
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status.HTTP_200_OK,
        )
    
    def deleted(message):
        return Response(
            {
                'success': True,
                'message': message,
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    def ok(message):
        return Response(
            {
                'success': True,
                'message': message,
            },
            status=status.HTTP_200_OK,
        )

    def bad_request(message):
        return Response(
            {
                'success': False,
                'message': message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    def not_found(message):
        return Response(
            {
                'success': False,
                'message': message,
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    
    def method_not_allowed(message):
        return Response(
            {
                'success': False,
                'message': message,
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def serializers_erros(errors):
        errors = errors.items()
        return Response(
            {
                'success': False,
                'message': [key for key, val in errors][0] + ': ' +  [val for key, val in errors][0][0],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )