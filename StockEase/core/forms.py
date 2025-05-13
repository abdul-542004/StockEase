from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Customer, Supplier, Category, Warehouse, Product



# --- User Forms ---

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email address',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name',
    }))
    role = forms.ChoiceField(choices=User._meta.get_field('role').choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }))

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        }),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }

class UserUpdateForm(UserChangeForm):
    password = None  # Hide password field in update
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email address',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'First name',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Last name',
    }))
    role = forms.ChoiceField(choices=User._meta.get_field('role').choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        }



# --- Customer Forms ---
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'telephone', 'address_street', 'address_city', 'address_postcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Customer Name'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Telephone'}),
            'address_street': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Street'}),
            'address_city': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'City'}),
            'address_postcode': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Postcode'}),
        }

# --- Supplier Forms ---
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['first_name', 'last_name', 'email', 'telephone', 'businessName', 'accountNumber', 'address_street', 'address_city', 'address_postcode']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Telephone'}),
            'businessName': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Business Name'}),
            'accountNumber': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Account Number'}),
            'address_street': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Street'}),
            'address_city': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'City'}),
            'address_postcode': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Postcode'}),
        }



# --- Category Form ---
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Category Title'}),
            'description': forms.Textarea(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Description', 'rows': 3}),
        }

# --- Warehouse Form ---
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'isRefrigerated', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Warehouse Name'}),
            'isRefrigerated': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
            'location': forms.Select(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'}),
        }

# --- Product Form ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['barCode', 'name', 'description', 'category', 'expiryDate',  'sellingPrice', 'packedWeight', 'packedHeight', 'packedWidth', 'packedDepth', 'refrigerated']
        widgets = {
            'barCode': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Barcode'}),
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'placeholder': 'Description', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'}),
            'expiryDate': forms.DateInput(attrs={'type': 'date', 'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400'}),
            'averageCostPrice': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'sellingPrice': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'packedWeight': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'packedHeight': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'packedWidth': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'packedDepth': forms.NumberInput(attrs={'class': 'input input-bordered w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400', 'step': '0.01'}),
            'refrigerated': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600'}),
        }