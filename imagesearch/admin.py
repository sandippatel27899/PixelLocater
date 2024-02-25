from django.contrib import admin
from .models import Image
from django.utils.html import format_html
# admin.site.register(Image)

class ImageAdmin(admin.ModelAdmin):

    def render_image(self, obj):
        return format_html(f'<img src="{obj.image.url}" width="50" height="50" />')
    
    list_display = ('render_image',)
    
admin.site.register(Image, ImageAdmin)