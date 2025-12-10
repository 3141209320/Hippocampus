from django.contrib import admin
from .models import ExamPaper, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('original_id', 'q_type', 'content', 'answer', 'score')
    readonly_fields = ('original_id', 'q_type', 'content', 'answer', 'score')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

from django.utils.html import format_html
from django.urls import reverse

@admin.register(ExamPaper)
class ExamPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner_display', 'is_public_display', 'created_at', 'get_question_count', 'practice_link')
    list_filter = ('is_public', 'created_at', 'owner')
    fields = ('title', 'source_file', 'owner', 'is_public', 'created_at')
    readonly_fields = ('created_at',)
    inlines = [QuestionInline]
    actions = ['make_public', 'make_private']
    
    def get_question_count(self, obj):
        return obj.question_set.count()
    get_question_count.short_description = "题目数量"

    def owner_display(self, obj):
        return obj.owner.username if obj.owner else "未知"
    owner_display.short_description = "上传者"
    
    def is_public_display(self, obj):
        if obj.is_public:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ 公开</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">🔒 私有</span>'
            )
    is_public_display.short_description = "可见性"

    def practice_link(self, obj):
        # Generate link to the exam detail page
        url = reverse('exam_detail', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #4f46e5; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">开始刷题 🚀</a>',
            url
        )
    practice_link.short_description = "操作"
    
    # 批量操作:设为公开
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'成功将 {updated} 个试卷设为公开')
    make_public.short_description = "✅ 设为公开(所有用户可见)"
    
    # 批量操作:设为私有
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'成功将 {updated} 个试卷设为私有')
    make_private.short_description = "🔒 设为私有(仅上传者可见)"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper', 'original_id', 'q_type', 'content_preview', 'score')
    list_filter = ('paper', 'q_type')
    search_fields = ('content', 'explanation')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "题目内容"
