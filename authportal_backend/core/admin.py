from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from .models import CustomUser, EBooklet, UserEBookletSelection

class CustomUserChangeForm(forms.ModelForm):
    ebooklet = forms.ModelMultipleChoiceField(
        queryset=EBooklet.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Ebooklets'
    )
    view_option = forms.ChoiceField(
        choices=(
            ('full', 'Full Access'),
            ('preview', 'Preview Only'),
            ('none', 'No Access'),
        ),
        required=False,
        label='Ebooklet View Option'
    )

    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            selected_ebooklets = UserEBookletSelection.objects.filter(user=self.instance).values_list('ebooklet', flat=True)
            self.fields['ebooklet'].initial = selected_ebooklets
            first_selection = UserEBookletSelection.objects.filter(user=self.instance).first()
            if first_selection:
                self.fields['view_option'].initial = first_selection.view_option
            else:
                self.fields['view_option'].initial = 'none'

    def save(self, commit=True):
        user = super().save(commit)
        if user.pk:
            # Delete existing selections
            user.userebookletselection_set.all().delete()
            # Create a single UserEBookletSelection record
            selection = UserEBookletSelection.objects.create(
                user=user,
                view_option=self.cleaned_data.get('view_option', 'none')
            )
            # Set the many-to-many ebooklet field
            selection.ebooklet.set(self.cleaned_data['ebooklet'])
            selection.save()
        return user

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active', 'phone_number', 'memberID', 'get_ebooklet_approved']
    search_fields = ['username', 'email', 'phone_number', 'memberID']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        ('Personal info', {'fields': ('username', 'email', 'phone_number', 'memberID')}),
        # Removed Permissions section as per user request
        # ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),  
    )

    def get_ebooklet_approved(self, obj):
        selections = obj.userebookletselection_set.all()
        ebooklet_names = [selection.ebooklet.all().first().name for selection in selections if selection.ebooklet.exists()]
        return ", ".join(ebooklet_names)
    get_ebooklet_approved.short_description = 'Approved E-Booklets'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('toggle-approval/<int:pk>/', self.admin_site.admin_view(self.toggle_approval_view), name='toggle-approval'),
        ]
        return custom_urls + urls

    def toggle_approval_view(self, request, pk):
        try:
            selection = UserEBookletSelection.objects.get(pk=pk)
            selection.approved = not selection.approved
            selection.save()
            self.message_user(request, f"Approval status toggled for {selection}", messages.SUCCESS)
        except UserEBookletSelection.DoesNotExist:
            self.message_user(request, "Selection not found.", messages.ERROR)
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))

try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass
admin.site.register(CustomUser, CustomUserAdmin)

from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from .utils import generate_pdf_page_images

@admin.register(EBooklet)
class EBookletAdmin(admin.ModelAdmin):
    list_display = ['name', 'pdf_file', 'static_pdf_filename']
    search_fields = ['name', 'static_pdf_filename']
    fields = ['name', 'pdf_file', 'static_pdf_filename']
    actions = ['generate_page_images']

    def generate_page_images(self, request, queryset):
        for ebooklet in queryset:
            try:
                generate_pdf_page_images(ebooklet)
                self.message_user(request, f"Page images generated for '{ebooklet.name}'.", messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Error generating images for '{ebooklet.name}': {e}", messages.ERROR)
    generate_page_images.short_description = "Generate page images for selected ebooklets"

class UserEBookletSelectionForm(forms.ModelForm):
    ebooklet = forms.ModelMultipleChoiceField(
        queryset=EBooklet.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Ebooklets'
    )

    class Meta:
        model = UserEBookletSelection
        fields = '__all__'

from django.db.models import Count, F, Value
from django.db.models.functions import Concat
from django.utils.html import format_html

@admin.register(UserEBookletSelection)
class UserEBookletSelectionAdmin(admin.ModelAdmin):
    form = UserEBookletSelectionForm
    list_display = ['user', 'get_ebooklets', 'payment_verified', 'approved', 'view_option', 'selected_at']
    list_filter = ['payment_verified', 'approved', 'view_option']
    search_fields = ['user__username', 'ebooklet__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Remove values() to avoid select_related() error
        # Instead, annotate ebooklet names using Subquery or ArrayAgg if supported
        # SQLite does not support ArrayAgg, fallback to simple queryset without aggregation
        return super().get_queryset(request)

    def get_ebooklets(self, obj):
        # obj can be a dict (annotated queryset) or model instance
        if isinstance(obj, dict):
            return ", ".join(obj.get('ebooklet_names', []))
        else:
            return ", ".join([ebooklet.name for ebooklet in obj.ebooklet.all()])
    get_ebooklets.short_description = 'Ebooklets'
