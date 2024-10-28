from django.contrib import admin
from .models import Feedback, EmailMessage

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'stars', 'category', 'feedback_mode', 'created_at')
    search_fields = ('user__email', 'comment', 'category')
    list_filter = ('stars', 'category', 'feedback_mode', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Feedback Details', {
            'fields': ('stars', 'comment', 'category', 'feedback_mode')
        }),
        ('Additional Information', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at',)

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'viewed')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at', 'viewed')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email')
        }),
        ('Message Details', {
            'fields': ('message',)
        }),
        ('Additional Information', {
            'fields': ('created_at', 'viewed'),
        }),
    )

    readonly_fields = ('created_at',)

admin.site.register(EmailMessage, EmailMessageAdmin)
admin.site.register(Feedback, FeedbackAdmin)
