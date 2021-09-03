import json
from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'hello/index.html')

@csrf_exempt
def compare(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        text1 = request_body['text1']
        text2 = request_body['text2']
        return JsonResponse({
            "text1": text1,
            "text2": text2
        })
    else:
        return HttpResponseNotFound('Woah!')