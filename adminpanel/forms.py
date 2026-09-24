from django import forms
from products.models import Product
from products.models import Comment
from orders.models import Order,OrderItem
from django.forms import inlineformset_factory
from products.models import Brand, Category, ProductImage, ProductSpecification


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'brand', 'category','description', 'short_description', 'price', 'active', 'image','stock','stock_status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body', 'stars', 'active']
        

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone_number',
            'address', 'order_notes', 'status', 'is_paid'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'order_notes': forms.Textarea(attrs={'rows': 3}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'وضعیت سفارش',
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

# inline formset برای ویرایش چند آیتم در همان فرم
OrderItemFormSet = inlineformset_factory(
    Order, OrderItem,
    form=OrderItemForm,
    extra=1,         # اجازه افزودن محصول جدید
    can_delete=True  # اجازه حذف آیتم
)


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'slug', 'description']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'slug', 'parent']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']

class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = ['name', 'value']
