from rest_framework.decorators import api_view
from django.http import JsonResponse


@api_view(['GET'])
def health_check(request):
    return JsonResponse(data={"msg":"pass"},status=200)
