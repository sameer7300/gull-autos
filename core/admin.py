from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib.admin.models import LogEntry
from .models import Category, Product, ProductImage, BlogPost, Testimonial, ContactMessage

class CustomAdminSite(admin.AdminSite):
    site_header = 'Gull Autos Administration'
    site_title = 'Gull Autos Admin'
    index_title = 'Dashboard'

admin_site = CustomAdminSite(name='customadmin')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'alt_text', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'status_label', 'is_featured', 'created_at')
    list_filter = ('category', 'created_at', 'stock', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    actions = ['mark_out_of_stock', 'mark_in_stock', 'toggle_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Visibility', {
            'fields': ('is_featured',)
        }),
    )

    def status_label(self, obj):
        if obj.stock <= 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.stock < 5:
            return format_html('<span style="color: orange;">Low Stock</span>')
        return format_html('<span style="color: green;">In Stock</span>')
    status_label.short_description = 'Status'

    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock=0)
    mark_out_of_stock.short_description = "Mark selected products as out of stock"

    def mark_in_stock(self, request, queryset):
        queryset.update(stock=10)
    mark_in_stock.short_description = "Mark selected products as in stock (10 items)"

    def toggle_featured(self, request, queryset):
        for product in queryset:
            product.is_featured = not product.is_featured
            product.save()
    toggle_featured.short_description = "Toggle featured status"

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'status', 'view_count']
    list_filter = ['status', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['publish_posts', 'unpublish_posts']
    
    def publish_posts(self, request, queryset):
        queryset.update(status='published')
    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        queryset.update(status='draft')
    unpublish_posts.short_description = "Unpublish selected posts"

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['name', 'role', 'company', 'message']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read', 'message_preview')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = {
            'total_products': Product.objects.count(),
            'low_stock_products': Product.objects.filter(stock__lt=5).count(),
            'total_orders': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
            'recent_activities': LogEntry.objects.all()[:5],
            'popular_categories': Category.objects.annotate(
                product_count=Count('products')
            ).order_by('-product_count')[:5],
            'title': 'Dashboard',
        }
        return render(request, 'admin/dashboard.html', context)
