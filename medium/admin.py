# admin.py
from django.contrib import admin
from .models import BlogPost, Category

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'views', 'created_at']
    list_filter = ['status', 'author', 'created_at']
    search_fields = ['title', 'author', 'tags']
    readonly_fields = ['views', 'created_at', 'updated_at']
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
