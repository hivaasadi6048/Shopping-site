# adminpanel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden, JsonResponse
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import messages
from django.core.paginator import Paginator
from products.models import Product, Comment
from products.models import Brand, Category, ProductImage, ProductSpecification
from orders.models import Order
from orders.utils import generate_invoice_screenshot
from .forms import ProductForm, OrderUpdateForm, CommentForm, OrderStatusForm, OrderItemFormSet
from .forms import BrandForm, CategoryForm, ProductImageForm, ProductSpecificationForm
from .decorators import staff_or_superuser_required, staff_required, superuser_required
from .utils import create_audit_log










@superuser_required
def home(request):
    return render(request, 'adminpanel/home_dashboard.html')

# -------- محصولات --------
@staff_or_superuser_required
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        create_audit_log(request, 'CREATE', product)
        return redirect('adminpanel:product_list')
    return render(request, 'adminpanel/product_form.html', {'form': form, 'title': 'Add Product'})


@staff_or_superuser_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)

    if not (request.user.is_superuser or product.owner == request.user):
        return HttpResponseForbidden("You are not allowed to edit this product.")

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', product)
        return redirect('adminpanel:product_list')
    return render(request, 'adminpanel/product_form.html', {'form': form, 'title': 'Edit Product'})


@superuser_required
@require_POST
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)

    if not (request.user.is_superuser or product.owner == request.user):
        return HttpResponseForbidden("You are not allowed to delete this product.")

    create_audit_log(request, 'DELETE', product)
    product.delete()
    return redirect('adminpanel:product_list')


@staff_required
def product_list(request):
    if request.user.is_superuser:
        products = Product.objects.all().order_by('-id')
    else:
        products = Product.objects.filter(owner=request.user).order_by('-id')

    # --- صفحه‌بندی ---
    paginator = Paginator(products, 10)  # ← تعداد محصول در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,   # همون products فعلیت ولی حالا صفحه‌بندی‌شده
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }    
    return render(request, 'adminpanel/product_list.html', context)


# -------- سفارش‌ها --------

@staff_required
def order_list(request):
    orders = Order.objects.all().order_by('-datetime_created')
    return render(request, 'adminpanel/order_list.html', {'orders': orders})

    

@superuser_required
@transaction.atomic
def order_update(request, id):
    """
    ویرایش سفارش + آیتم‌ها با بروزرسانی موجودی انبار و تولید مجدد فاکتور PDF
    """
    order = get_object_or_404(Order, id=id)
    form = OrderUpdateForm(request.POST or None, instance=order)
    formset = OrderItemFormSet(request.POST or None, instance=order)

    # محصولات برای JSON (استفاده در JS)
    products_data = list(Product.objects.filter(active=True).values('id','price','title','stock'))
    products_json = json.dumps(products_data, cls=DjangoJSONEncoder)

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            form.save()

            # ذخیره آیتم‌ها با مدیریت موجودی کالا
            old_items = {item.id: item.quantity for item in order.items.all()}
            items = formset.save(commit=False)

            for item in items:
                item.order = order
                old_quantity = old_items.get(item.id, 0)
                quantity_diff = item.quantity - old_quantity

                if quantity_diff != 0:
                    product = item.product
                    # بروزرسانی موجودی محصول
                    product.stock = max(product.stock - quantity_diff, 0)
                    product.save()

                item.save()

            # آیتم‌هایی که حذف شده‌اند:
            for deleted_item in formset.deleted_objects:
                product = deleted_item.product
                product.stock += deleted_item.quantity
                product.save()
                deleted_item.delete()

            formset.save_m2m()

            # فاکتور جدید و PDF به‌روزرسانی شود
            try:
                invoice = order.create_invoice()
                generate_invoice_screenshot(order)
            except Exception as e:
                print("❌ خطا در تولید فاکتور:", e)

            # ثبت لاگ و پیام موفقیت
            create_audit_log(request, 'UPDATE', order)
            messages.success(request, "✅ سفارش و محصولات با موفقیت ذخیره و بروزرسانی شدند.")
            return redirect('adminpanel:order_list')
        else:
            messages.error(request, "⚠️ لطفاً خطاهای فرم را بررسی کنید.")

    context = {
        'order': order,
        'form': form,
        'formset': formset,
        'products_json': products_json,
    }
    return render(request, 'adminpanel/order_update.html', context)





@superuser_required
@require_POST
def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    create_audit_log(request, 'DELETE', order)
    order.delete()
    return redirect('adminpanel:order_list')


@superuser_required
@transaction.atomic
def order_status_update(request, id):
    order = get_object_or_404(Order, id=id)
    form = OrderStatusForm(request.POST or None, instance=order)
    
    if form.is_valid():
        old_status = order.status
        form.save()
        new_status = order.status
        create_audit_log(
            request,
            'STATUS_CHANGE',
            order,
            extra_info=f"Status changed from {old_status} to {new_status}"
        )
        return redirect('adminpanel:order_list')

    return render(request, 'adminpanel/order_status_update.html', {'order': order, 'form': form, 'title': 'Change Order Status'})


# -------- کامنت‌ها --------

@superuser_required
def comment_list(request):
    comments = Comment.objects.all().order_by('-datetime_created')
    return render(request, 'adminpanel/comment_list.html', {'comments': comments})

@superuser_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.product = product
            comment.save()
            create_audit_log(request, 'CREATE', comment)
            return redirect('adminpanel:comment_list')
    else:
        form = CommentForm()
    return render(request, 'adminpanel/comment_form.html', {'form': form, 'product': product})


@superuser_required
@transaction.atomic
def comment_edit(request, id):
    comment = get_object_or_404(Comment, id=id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', comment)
        return redirect('adminpanel:comment_list')
    return render(request, 'adminpanel/comment_form.html', {'form': form, 'comment': comment})


@superuser_required
@require_POST
def comment_delete(request, id):
    comment = get_object_or_404(Comment, id=id)
    create_audit_log(request, 'DELETE', comment)
    comment.delete()
    return redirect('adminpanel:comment_list')





# ---- برندها ----
@superuser_required
def brand_list(request):
    brands = Brand.objects.all()
    return render(request, 'adminpanel/brand_list.html', {'brands': brands})

@superuser_required
def brand_add(request):
    form = BrandForm(request.POST or None)
    if form.is_valid():
        brand = form.save()
        create_audit_log(request, 'CREATE', brand)
        return redirect('adminpanel:brand_list')
    return render(request, 'adminpanel/brand_form.html', {'form': form})

@superuser_required
@transaction.atomic
def brand_edit(request, id):
    brand = get_object_or_404(Brand, id=id)
    form = BrandForm(request.POST or None, instance=brand)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', brand)
        return redirect('adminpanel:brand_list')
    return render(request, 'adminpanel/brand_form.html', {'form': form, 'title': 'Edit Brand'})

@require_POST
@superuser_required
def brand_delete(request, id):
    brand = get_object_or_404(Brand, id=id)
    create_audit_log(request, 'DELETE', brand)
    brand.delete()
    return redirect('adminpanel:brand_list')


# ---- دسته‌بندی‌ها ----
@superuser_required
def category_list(request):
    categories = Category.objects.all().order_by('order', 'title')
    tree = build_category_tree(categories)
    return render(request, 'adminpanel/category_list.html', {'tree': tree})

@superuser_required
def category_add(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        cat = form.save()
        create_audit_log(request, 'CREATE', cat)
        return redirect('adminpanel:category_list')
    return render(request, 'adminpanel/category_form.html', {'form': form})

@superuser_required
@transaction.atomic
def category_edit(request, id):
    cat = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, instance=cat)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', cat)
        return redirect('adminpanel:category_list')
    return render(request, 'adminpanel/category_form.html', {'form': form, 'title': 'Edit Category'})

@require_POST
@superuser_required
def category_delete(request, id):
    cat = get_object_or_404(Category, id=id)
    create_audit_log(request, 'DELETE', cat)
    cat.delete()
    return redirect('adminpanel:category_list')


def build_category_tree(categories):
    tree = []
    lookup = {}

    for category in categories:
        category.children_list = []
        lookup[category.id] = category

    for category in categories:
        if category.parent_id:
            lookup[category.parent_id].children_list.append(category)
        else:
            tree.append(category)

    return tree




@require_POST
@superuser_required
def save_category_tree(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not validate_tree_structure(data):
        return JsonResponse({"error": "Invalid tree structure (loop detected)"}, status=400)

    with transaction.atomic():
        update_tree(data, parent=None)

    return JsonResponse({"status": "success"})


def validate_tree_structure(nodes, visited=None):
    if visited is None:
        visited = set()

    for node in nodes:
        node_id = int(node["id"])

        if node_id in visited:
            return False

        visited.add(node_id)

        if not validate_tree_structure(node.get("children", []), visited.copy()):
            return False

    return True



def update_tree(nodes, parent):
    for index, node in enumerate(nodes):
        category = Category.objects.get(id=node["id"])
        category.parent = parent
        category.order = index
        category.save()

        update_tree(node.get("children", []), category)




# ---------------- تصاویر محصول ---------------- #

@superuser_required
def product_images_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()  # related_name در مدل
    return render(request, 'adminpanel/product_images_list.html', {
        'product': product,
        'images': images,
    })


@superuser_required
def product_image_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        image = form.save(commit=False)
        image.product = product
        image.save()
        create_audit_log(request, 'CREATE', image)
        return redirect('adminpanel:product_images_list', product_id=product.id)
    return render(request, 'adminpanel/product_image_form.html', {
        'form': form,
        'product': product,
        'title': 'Add Product Image',
    })


@superuser_required
@transaction.atomic
def product_image_edit(request, id):
    image = get_object_or_404(ProductImage, id=id)
    form = ProductImageForm(request.POST or None, request.FILES or None, instance=image)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', image)
        return redirect('adminpanel:product_images_list', product_id=image.product.id)
    return render(request, 'adminpanel/product_image_form.html', {
        'form': form,
        'product': image.product,
        'title': 'Edit Product Image',
    })


@superuser_required
@require_POST
def product_image_delete(request, id):
    image = get_object_or_404(ProductImage, id=id)
    product_id = image.product.id
    create_audit_log(request, 'DELETE', image)
    image.delete()
    return redirect('adminpanel:product_images_list', product_id=product_id)




# ---------------- مشخصات فنی محصول ---------------- #

@superuser_required
def product_specs_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    specs = product.specifications.all()  # related_name
    return render(request, 'adminpanel/product_specs_list.html', {
        'product': product,
        'specs': specs,
    })


@superuser_required
def product_spec_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductSpecificationForm(request.POST or None)
    if form.is_valid():
        spec = form.save(commit=False)
        spec.product = product
        spec.save()
        create_audit_log(request, 'CREATE', spec)
        return redirect('adminpanel:product_specs_list', product_id=product.id)
    return render(request, 'adminpanel/product_spec_form.html', {
        'form': form,
        'product': product,
        'title': 'Add Product Specification',
    })


@superuser_required
@transaction.atomic
def product_spec_edit(request, id):
    spec = get_object_or_404(ProductSpecification, id=id)
    form = ProductSpecificationForm(request.POST or None, instance=spec)
    if form.is_valid():
        form.save()
        create_audit_log(request, 'UPDATE', spec)
        return redirect('adminpanel:product_specs_list', product_id=spec.product.id)
    return render(request, 'adminpanel/product_spec_form.html', {
        'form': form,
        'product': spec.product,
        'title': 'Edit Product Specification',
    })


@superuser_required
@require_POST
def product_spec_delete(request, id):
    spec = get_object_or_404(ProductSpecification, id=id)
    product_id = spec.product.id
    create_audit_log(request, 'DELETE', spec)
    spec.delete()
    return redirect('adminpanel:product_specs_list', product_id=product_id)
