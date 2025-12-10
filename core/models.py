from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class ExamPaper(models.Model):
    title = models.CharField(_("试卷标题"), max_length=200)
    source_file = models.FileField(_("源文件"), upload_to='uploads/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("上传者"), null=True, blank=True)
    is_public = models.BooleanField(_("公开"), default=False, help_text="勾选后所有用户可见,取消勾选则仅上传者可见")
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("试卷")
        verbose_name_plural = _("试卷")
        
    def __str__(self):
        return self.title

class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = 'single_choice', _('单选题')
        MULTI = 'multi_choice', _('多选题')
        TRUE_FALSE = 'true_false', _('判断题')
        ESSAY = 'essay', _('简答题')
        FILL = 'fill_blank', _('填空题')
        UNKNOWN = 'unknown', _('未知')

    paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, verbose_name=_("所属试卷"))
    original_id = models.IntegerField(_("题号"), help_text="原始试卷中的题号")
    q_type = models.CharField(_("题型"), max_length=20, choices=QuestionType.choices, default=QuestionType.UNKNOWN)
    content = models.TextField(_("题目内容"))
    options = models.JSONField(_("选项 (JSON)"), null=True, blank=True, help_text='例如: [{"label":"A","content":"选项内容"}]')
    answer = models.TextField(_("参考答案"), blank=True)
    explanation = models.TextField(_("解析"), blank=True)
    score = models.FloatField(_("分值"), default=0)

    class Meta:
        verbose_name = _("题目")
        verbose_name_plural = _("题目列表")
        ordering = ['original_id']

    def __str__(self):
        return f"{self.original_id}. {self.content[:30]}..."

# --- User Progress & Mistakes ---
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("用户"))
    paper = models.ForeignKey(ExamPaper, on_delete=models.CASCADE, verbose_name=_("试卷"))
    current_index = models.IntegerField(_("当前进度"), default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'paper')

class UserMistake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("用户"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("题目"))
    mistake_count = models.IntegerField(_("错误次数"), default=1)
    last_mistake_time = models.DateTimeField(_("最近错误时间"), auto_now=True)
    note = models.TextField(_("错题笔记"), blank=True)
    
    class Meta:
        unique_together = ('user', 'question')

# --- Signals ---
from django.db.models.signals import post_save
from django.dispatch import receiver
from .parser import parse_exam_file

@receiver(post_save, sender=ExamPaper)
def auto_parse_paper(sender, instance, created, **kwargs):
    if created and instance.source_file:
        try:
            file_path = instance.source_file.path
            print(f"Start parsing file: {file_path}")
            
            questions_data = parse_exam_file(file_path)
            
            questions_to_create = []
            for q in questions_data:
                questions_to_create.append(Question(
                    paper=instance,
                    original_id=q['original_id'],
                    q_type=q['type'],
                    content=q['content'],
                    options=q['options'] if q['options'] else None,
                    answer=q['answer'],
                    explanation=q['explanation'],
                    score=q['score']
                ))
            
            Question.objects.bulk_create(questions_to_create)
            print(f"Successfully parsed and created {len(questions_to_create)} questions for paper {instance.id}")
            
        except Exception as e:
            print(f"Error parsing paper {instance.id}: {e}")
