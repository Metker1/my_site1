from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, Idea


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'post_count']

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = 'Статей'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'status_badge', 'created', 'views', 'image_preview']
    list_filter = ['category', 'created', 'status']
    search_fields = ['title', 'short_text', 'full_text']
    list_editable = ['status']
    actions = ['make_published', 'make_rejected', 'make_draft']

    fieldsets = (
        ('Основное', {
            'fields': ('title', 'short_text', 'full_text', 'category', 'image'),
            'classes': ('wide', 'extrapretty'),
        }),
        ('Статус', {
            'fields': ('status',),
            'classes': ('collapse', 'wide'),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'published': 'success',
            'rejected': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div class="image-preview"><img src="{}" width="50" height="50" style="object-fit: cover;"></div>',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Картинка'

    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} постов опубликовано', 'success')

    make_published.short_description = "Опубликовать выбранные посты"

    def make_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} постов отклонено', 'warning')

    make_rejected.short_description = "Отклонить выбранные посты"

    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} постов переведено в черновики', 'info')

    make_draft.short_description = "В черновики"

    class Media:
        css = {
            'all': ('admin/css/admin_style.css',)
        }


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'status_badge', 'created', 'updated']
    list_filter = ['status', 'created', 'author']
    search_fields = ['title', 'description', 'notes']
    list_editable = ['status']
    readonly_fields = ['author', 'created', 'updated']
    actions = ['make_accepted', 'make_rejected', 'make_implemented', 'make_under_review']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'author'),
            'classes': ('wide',),
        }),
        ('Статус и комментарии', {
            'fields': ('status', 'notes'),
            'classes': ('wide',),
        }),
        ('Даты', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'proposed': 'primary',
            'under_review': 'warning',
            'accepted': 'info',
            'rejected': 'danger',
            'implemented': 'success'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус идеи'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def make_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'{updated} идей принято', 'success')

    make_accepted.short_description = "Принять выбранные идеи"

    def make_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} идей отклонено', 'warning')

    make_rejected.short_description = "Отклонить выбранные идеи"

    def make_implemented(self, request, queryset):
        updated = queryset.update(status='implemented')
        self.message_user(request, f'{updated} идей отмечено как реализованные', 'success')

    make_implemented.short_description = "Отметить как реализованные"

    def make_under_review(self, request, queryset):
        updated = queryset.update(status='under_review')
        self.message_user(request, f'{updated} идей переведены на рассмотрение', 'info')

    make_under_review.short_description = "Перевести на рассмотрение"

    class Media:
        css = {
            'all': ('admin/css/admin_style.css',)
        }