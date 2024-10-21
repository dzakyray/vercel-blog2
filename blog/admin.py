from django.contrib import admin
from .models import Post
from .models import Post, Category  # Pastikan Category diimpor dengan benar
from taggit.models import Tag

class TagListFilter(admin.SimpleListFilter):
    title = 'Tag'
    parameter_name = 'tag'

    def lookups(self, request, model_admin):
        """Menampilkan opsi tag di filter."""
        tags = Tag.objects.all()
        return [(tag.name, tag.name) for tag in tags]

    def queryset(self, request, queryset):
        """Filter postingan berdasarkan tag yang dipilih."""
        if self.value():
            return queryset.filter(tags__name__in=[self.value()])
        return queryset

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'category')
    list_filter = ('status', 'created', 'publish', 'author', 'category', TagListFilter)  # Tambahkan filter kustom
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
    actions = ['delete_selected']
