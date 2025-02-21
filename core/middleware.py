from django.urls import resolve
from .models import Product, BlogPost

class ViewCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only track views for successful GET requests
        if request.method == 'GET' and response.status_code == 200:
            resolved_path = resolve(request.path_info)
            
            # Track product views
            if resolved_path.url_name == 'product_detail':
                product_slug = resolved_path.kwargs.get('product_slug')
                if product_slug:
                    Product.objects.filter(slug=product_slug).update(view_count=models.F('view_count') + 1)
            
            # Track blog post views
            elif resolved_path.url_name == 'blog_detail':
                post_slug = resolved_path.kwargs.get('post_slug')
                if post_slug:
                    BlogPost.objects.filter(slug=post_slug).update(view_count=models.F('view_count') + 1)
        
        return response
