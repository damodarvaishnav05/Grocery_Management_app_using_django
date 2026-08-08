from django.shortcuts import render


def index(request):
    """Placeholder view — inventory will be added in Stage 10."""
    return render(request, 'inventory/index.html')
