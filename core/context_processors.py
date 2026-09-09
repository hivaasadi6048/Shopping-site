from products.models import Category

def categories_processor(request):
    categories = Category.objects.filter(
        parent=None
    ).prefetch_related(
        'children__children'
    )

    return {
        'categories': categories
    }