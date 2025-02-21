from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Product, Category, BlogPost, Testimonial, Contact, Newsletter, ProductImage, ContactMessage, AdminNotification
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
import uuid
from datetime import datetime

def superuser_required(user):
    return user.is_authenticated and user.is_superuser

def staff_member_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, displaying an error message if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='admin_login'
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, 'Welcome back, Admin!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    
    return render(request, 'admin/login.html')

def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')

@user_passes_test(superuser_required, login_url='admin_login')
def admin_dashboard(request):
    # Get statistics for the dashboard
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get unread messages count
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    # Create notification for unread messages if there are any
    if unread_messages > 0:
        create_notification(
            user=request.user,
            notification_type='contact',
            message=f'You have {unread_messages} unread messages',
            link=reverse('admin_contact_messages')
        )
    
    # Get low stock products and create notifications
    low_stock_products = Product.objects.filter(stock__lt=10)
    for product in low_stock_products:
        create_notification(
            user=request.user,
            notification_type='product',
            message=f'Low stock alert: {product.name} has only {product.stock} items left',
            link=reverse('admin_products')
        )
    
    # Get pending testimonials and create notifications
    pending_testimonials = Testimonial.objects.filter(is_approved=False)
    for testimonial in pending_testimonials:
        create_notification(
            user=request.user,
            notification_type='testimonial',
            message=f'New testimonial from {testimonial.name} needs approval',
            link=reverse('admin_testimonials')
        )
    
    context = {
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_blog_posts': BlogPost.objects.count(),
        'total_testimonials': Testimonial.objects.count(),
        'recent_products': Product.objects.order_by('-created_at')[:5],
        'recent_testimonials': Testimonial.objects.order_by('-created_at')[:5],
        'recent_blog_posts': BlogPost.objects.order_by('-created_at')[:5],
        'pending_testimonials': pending_testimonials.count(),
        'low_stock_products': low_stock_products.count(),
        'unread_messages': unread_messages,
        'monthly_stats': {
            'products': Product.objects.filter(created_at__gte=thirty_days_ago).count(),
            'testimonials': Testimonial.objects.filter(created_at__gte=thirty_days_ago).count(),
            'blog_posts': BlogPost.objects.filter(created_at__gte=thirty_days_ago).count(),
            'messages': ContactMessage.objects.filter(created_at__gte=thirty_days_ago).count(),
        }
    }
    
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(superuser_required, login_url='admin_login')
def admin_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin/products.html', {'products': products})

@user_passes_test(superuser_required, login_url='admin_login')
def admin_testimonials(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    return render(request, 'admin/testimonials.html', {'testimonials': testimonials})

@user_passes_test(superuser_required, login_url='admin_login')
def admin_blog_posts(request):
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Handle status filter
    status_filter = request.GET.get('status')
    if status_filter:
        blog_posts = blog_posts.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(blog_posts, 10)  # Show 10 posts per page
    page = request.GET.get('page')
    try:
        blog_posts = paginator.page(page)
    except PageNotAnInteger:
        blog_posts = paginator.page(1)
    except EmptyPage:
        blog_posts = paginator.page(paginator.num_pages)
    
    context = {
        'blog_posts': blog_posts,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/blog_posts.html', context)

@user_passes_test(superuser_required, login_url='admin_login')
def admin_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'admin/categories.html', {'categories': categories})

def home(request):
    context = {
        'featured_products': Product.objects.all()[:6],  # Get first 6 products
        'testimonials': Testimonial.objects.all()[:3],   # Get first 3 testimonials
        'categories': Category.objects.all()[:4],        # Get first 4 categories
    }
    return render(request, 'home.html', context)

class AboutView(TemplateView):
    template_name = 'about.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_contact_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'admin/contact_messages.html', {'messages': messages})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_contact_message_detail(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    return JsonResponse({
        'id': message.id,
        'name': message.name,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_read': message.is_read
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_contact_message_mark_read(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(ContactMessage, pk=pk)
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_contact_message_delete(request, pk):
    if request.method == 'POST':
        message = get_object_or_404(ContactMessage, pk=pk)
        message.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'contact.html')

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Get category from URL slug or query parameter
        category_slug = self.kwargs.get('category_slug')
        category_id = self.request.GET.get('category')
        
        if category_slug:
            # Filter by category slug from URL
            queryset = queryset.filter(category__slug=category_slug)
        elif category_id:
            # Filter by category ID from query parameter
            try:
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass  # Invalid category ID, return all products
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related products from the same category
        related_products = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:3]
        context['related_products'] = related_products
        return context

class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'

    def get_queryset(self):
        # Only show published posts unless user is staff
        if self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status='published')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff:
            obj.view_count += 1
            obj.save()
        return obj

class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(status='published').order_by('-created_at')

def global_search(request):
    query = request.GET.get('q', '')
    results = {
        'products': [],
        'categories': [],
        'blog_posts': [],
        'testimonials': [],
        'total_count': 0
    }
    
    if query:
        # Search in products
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        
        # Search in categories
        categories = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        
        # Search in blog posts
        blog_posts = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).filter(status='published').distinct()
        
        # Search in testimonials
        testimonials = Testimonial.objects.filter(
            Q(name__icontains=query) |
            Q(message__icontains=query) |
            Q(company__icontains=query) |
            Q(role__icontains=query)
        ).filter(is_approved=True).distinct()
        
        results = {
            'products': products,
            'categories': categories,
            'blog_posts': blog_posts,
            'testimonials': testimonials,
            'total_count': (
                products.count() + 
                categories.count() + 
                blog_posts.count() + 
                testimonials.count()
            ),
            'query': query
        }
    
    if request.headers.get('HX-Request'):
        # Return partial template for AJAX requests
        return render(request, 'partials/search_results.html', results)
    
    # Return full template for direct visits
    return render(request, 'search_results.html', results)

def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            # Validate email format
            validate_email(email)
            
            # Check if email already exists
            if Newsletter.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'This email is already subscribed to our newsletter.'
                })
            
            # Create new subscription
            Newsletter.objects.create(email=email)
            
            # Send welcome email
            subject = 'Welcome to Gull Autos Newsletter!'
            message = f'''
            Thank you for subscribing to our newsletter!
            
            Stay tuned for the latest updates about our products, special offers, and automotive news.
            
            Best regards,
            Gull Autos Team
            '''
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't prevent subscription
                print(f"Error sending welcome email: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!'
            })
            
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again later.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

def testimonial_submit(request):
    if request.method == 'POST':
        try:
            testimonial = Testimonial.objects.create(
                name=request.POST.get('name'),
                role=request.POST.get('role'),
                company=request.POST.get('company'),
                message=request.POST.get('message'),
                rating=request.POST.get('rating'),
            )
            if 'image' in request.FILES:
                testimonial.image = request.FILES['image']
                testimonial.save()
            
            messages.success(request, 'Thank you for your testimonial! It will be reviewed and published soon.')
            return redirect('testimonials')
        except Exception as e:
            messages.error(request, 'There was an error submitting your testimonial. Please try again.')
            return redirect('testimonials')
    
    return redirect('testimonials')

def testimonials_view(request):
    testimonials = Testimonial.objects.filter(is_approved=True)
    return render(request, 'testimonials.html', {
        'testimonials': testimonials
    })

def terms_of_service(request):
    return render(request, 'policies/terms.html')

def privacy_policy(request):
    return render(request, 'policies/privacy.html')

def cookie_policy(request):
    return render(request, 'policies/cookies.html')

# Admin Product Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_product_create(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            sku = request.POST.get('sku')
            category_id = request.POST.get('category')
            
            # Create the product
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=stock,
                sku=sku,
                category_id=category_id
            )
            
            # Handle images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            messages.success(request, 'Product created successfully!')
            return redirect('admin_products')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'admin/product_form.html', {
        'action': 'Create',
        'categories': categories
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.price = request.POST.get('price')
            product.stock = request.POST.get('stock')
            product.sku = request.POST.get('sku')
            product.category_id = request.POST.get('category')
            product.save()
            
            # Handle images
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'admin/product_form.html', {
        'product': product,
        'action': 'Edit',
        'categories': categories
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_product_delete(request, pk):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=pk)
            product.delete()
            messages.success(request, 'Product deleted successfully!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_product_image_delete(request, pk):
    if request.method == 'POST':
        try:
            image = get_object_or_404(ProductImage, pk=pk)
            # Delete the actual image file
            if image.image:
                image.image.delete()
            # Delete the database record
            image.delete()
            messages.success(request, 'Product image deleted successfully!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# Admin Category Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Category.objects.create(name=name)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_category_edit(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        category.name = request.POST.get('name')
        category.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_category_delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

# Admin Blog Post Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_blog_post_create(request):
    if request.method == 'POST':
        try:
            blog_post = BlogPost.objects.create(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                excerpt=request.POST.get('excerpt'),
                author_id=request.POST.get('author'),
                status=request.POST.get('status', 'draft')
            )
            
            if 'featured_image' in request.FILES:
                blog_post.featured_image = request.FILES['featured_image']
                blog_post.save()
            
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_blog_posts')
        except Exception as e:
            messages.error(request, f'Error creating blog post: {str(e)}')
    
    users = User.objects.filter(is_staff=True)
    return render(request, 'admin/blog_post_form.html', {
        'action': 'Create',
        'users': users,
        'default_author': request.user
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_blog_post_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        try:
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            post.excerpt = request.POST.get('excerpt')
            post.author_id = request.POST.get('author')
            post.status = request.POST.get('status', 'draft')
            
            if 'featured_image' in request.FILES:
                # Delete old image if it exists
                if post.featured_image:
                    post.featured_image.delete()
                post.featured_image = request.FILES['featured_image']
            
            post.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_blog_posts')
        except Exception as e:
            messages.error(request, f'Error updating blog post: {str(e)}')
    
    users = User.objects.filter(is_staff=True)
    return render(request, 'admin/blog_post_form.html', {
        'post': post,
        'action': 'Edit',
        'users': users
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_blog_post_delete(request, pk):
    if request.method == 'POST':
        try:
            post = get_object_or_404(BlogPost, pk=pk)
            post.delete()
            messages.success(request, 'Blog post deleted successfully!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_blog_post_publish(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, pk=pk)
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_blog_post_image_delete(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, pk=pk)
        if post.image:
            post.image.delete()
            post.image = None
            post.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

# Admin Testimonial Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_testimonial_approve(request, pk):
    if request.method == 'POST':
        testimonial = get_object_or_404(Testimonial, pk=pk)
        testimonial.is_approved = True
        testimonial.save()
        
        # Create notification for approved testimonial
        create_notification(
            user=request.user,
            notification_type='testimonial',
            message=f'Testimonial from {testimonial.name} has been approved',
            link=reverse('admin_testimonials')
        )
        
        messages.success(request, 'Testimonial approved successfully!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_testimonials(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    return render(request, 'admin/testimonials.html', {'testimonials': testimonials})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_testimonial_delete(request, pk):
    if request.method == 'POST':
        testimonial = get_object_or_404(Testimonial, pk=pk)
        testimonial.delete()
        messages.success(request, 'Testimonial deleted successfully!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

# Admin Notification Views
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_notifications(request):
    notifications = AdminNotification.objects.filter(user=request.user)
    return render(request, 'admin/notifications.html', {'notifications': notifications})

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_notification_mark_read(request, pk):
    if request.method == 'POST':
        notification = get_object_or_404(AdminNotification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_notification_mark_all_read(request):
    if request.method == 'POST':
        AdminNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_profile(request):
    if request.method == 'POST':
        # Update profile
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('admin_profile')
    return render(request, 'admin/profile.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_security(request):
    if request.method == 'POST':
        # Change password
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please log in again.')
            return redirect('admin_login')
    return render(request, 'admin/security.html')

def create_notification(user, notification_type, message, link):
    """Helper function to create notifications"""
    notification = AdminNotification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        link=link
    )
    return notification
