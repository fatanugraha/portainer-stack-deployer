from django.contrib import admin
from app.models import Stack, Meta

class MetaInlineAdmin(admin.TabularInline):
    model = Meta
    extra = 0

class StackAdmin(admin.ModelAdmin):
    inlines = [MetaInlineAdmin]

admin.site.register(Stack, StackAdmin)
