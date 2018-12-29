from django.contrib import admin
from .models import Game, Move


# Updates the display in the admin interface
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_player', 'second_player', 'status')  # display items in admin site
    list_editable = ('status',)  # makes this item editable in the admin section


admin.site.register(Move)
