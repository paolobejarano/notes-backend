from django.contrib import admin
from .models import Category, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'created_at', 'updated_at']
    list_filter = ['category', 'created_at', 'updated_at']
    search_fields = ['title', 'body', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Note Information', {
            'fields': ('title', 'body', 'category')
        }),
        ('User & Timestamps', {
            'fields': ('user', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
