from django.core import serializers
from django.shortcuts import render

def index(request):

    return render(request, 'core/index.html')

def preview(request):
    
    # width = request.GET.get("width", 800)
    # height = request.GET.get("height", 600)

    # context = {
    #     "width": width,
    #     "height": height,
    # }

    return render(request, "core/preview_modal.html")
