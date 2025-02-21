from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.terms_of_service, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('cookies/', views.cookie_policy, name='cookies'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.global_search, name='global_search'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('products/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:post_slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('testimonials/', views.testimonials_view, name='testimonials'),
    path('testimonials/submit/', views.testimonial_submit, name='testimonial_submit'),
    # Admin URLs
    path('dashboard/login/', views.admin_login, name='admin_login'),
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/products/create/', views.admin_product_create, name='admin_product_create'),
    path('dashboard/products/<int:pk>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('dashboard/products/<int:pk>/delete/', views.admin_product_delete, name='admin_product_delete'),
    path('dashboard/products/images/<int:pk>/delete/', views.admin_product_image_delete, name='admin_product_image_delete'),
    
    path('dashboard/categories/', views.admin_categories, name='admin_categories'),
    path('dashboard/categories/create/', views.admin_category_create, name='admin_category_create'),
    path('dashboard/categories/<int:pk>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    path('dashboard/blog-posts/', views.admin_blog_posts, name='admin_blog_posts'),
    path('dashboard/blog-posts/create/', views.admin_blog_post_create, name='admin_blog_post_create'),
    path('dashboard/blog-posts/<int:pk>/edit/', views.admin_blog_post_edit, name='admin_blog_post_edit'),
    path('dashboard/blog-posts/<int:pk>/delete/', views.admin_blog_post_delete, name='admin_blog_post_delete'),
    path('dashboard/blog-posts/<int:pk>/publish/', views.admin_blog_post_publish, name='admin_blog_post_publish'),
    path('dashboard/blog-posts/<int:pk>/delete-image/', views.admin_blog_post_image_delete, name='admin_blog_post_image_delete'),
    
    # Testimonial URLs
    path('dashboard/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    path('dashboard/testimonials/<int:pk>/approve/', views.admin_testimonial_approve, name='admin_testimonial_approve'),
    path('dashboard/testimonials/<int:pk>/delete/', views.admin_testimonial_delete, name='admin_testimonial_delete'),
    
    # Contact Messages URLs
    path('dashboard/contact-messages/', views.admin_contact_messages, name='admin_contact_messages'),
    path('dashboard/contact-messages/<int:pk>/', views.admin_contact_message_detail, name='admin_contact_message_detail'),
    path('dashboard/contact-messages/<int:pk>/mark-read/', views.admin_contact_message_mark_read, name='admin_contact_message_mark_read'),
    path('dashboard/contact-messages/<int:pk>/delete/', views.admin_contact_message_delete, name='admin_contact_message_delete'),

    # Notification URLs
    path('dashboard/notifications/', views.admin_notifications, name='admin_notifications'),
    path('dashboard/notifications/<int:pk>/mark-read/', views.admin_notification_mark_read, name='admin_notification_mark_read'),
    path('dashboard/notifications/mark-all-read/', views.admin_notification_mark_all_read, name='admin_notification_mark_all_read'),

    # Profile and Security URLs
    path('dashboard/profile/', views.admin_profile, name='admin_profile'),
    path('dashboard/security/', views.admin_security, name='admin_security'),
]
