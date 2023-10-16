from django.contrib import admin

# Register your models here.
from .models import FCMToken,User,Opening



#make user name visible in admin panel
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type')
    list_filter = ('user_type',)
    search_fields = ['email']
    ordering = ('email',)

admin.site.register(User, UserAdmin)

class tokenAdmin(admin.ModelAdmin):
    list_display = [ 'user','created_at','last_updated']
    list_filter = ('user',)
    search_fields = ['user']
    ordering = ('created_at',)

admin.site.register(FCMToken, tokenAdmin)


admin.site.register(Opening)