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
    list_display = ('title', 'owner_display', 'created_at', 'get_question_count', 'practice_link')
    inlines = [QuestionInline]
    
    def get_question_count(self, obj):
        return obj.question_set.count()
    get_question_count.short_description = "题目数量"

    def owner_display(self, obj):
        return obj.owner
    owner_display.short_description = "上传者"

    def practice_link(self, obj):
        # Generate link to the exam detail page
        url = reverse('exam_detail', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #4f46e5; color: white; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">开始刷题 🚀</a>',
            url
        )
    practice_link.short_description = "操作"

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper', 'original_id', 'q_type', 'content_preview', 'score')
    list_filter = ('paper', 'q_type')
    search_fields = ('content', 'explanation')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "题目内容"
