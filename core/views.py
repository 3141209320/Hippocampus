from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExamPaper, Question, UserMistake, UserProgress
from .forms import ExamPaperForm
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if request.user.is_authenticated:
        return redirect('exam_list')
    return redirect('login')

@login_required
def upload_exam(request):
    if request.method == 'POST':
        form = ExamPaperForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.owner = request.user
            # 如果是管理员上传,自动设为公开
            if request.user.is_superuser or request.user.is_staff:
                paper.is_public = True
            paper.save()
            # Parsing is triggered by post_save signal automatically
            return redirect('exam_detail', paper_id=paper.id)
    else:
        form = ExamPaperForm()
    return render(request, 'core/upload_exam.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('exam_list')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect('exam_list')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    # Handle GET request for logout gracefully (optional, but good for UX links)
    logout(request) 
    return redirect('login')

@login_required
def exam_list(request):
    """
    试卷列表:显示用户可见的试卷
    - 公开的试卷(is_public=True)
    - 用户自己上传的试卷
    """
    from django.db.models import Q
    
    papers = ExamPaper.objects.filter(
        Q(is_public=True) | Q(owner=request.user)
    ).order_by('-created_at')
    
    return render(request, 'core/exam_list.html', {'papers': papers})

@login_required
def exam_detail(request, paper_id):
    paper = get_object_or_404(ExamPaper, id=paper_id)
    questions = paper.question_set.all().order_by('original_id')
    
    # Get user progress for this paper
    progress, created = UserProgress.objects.get_or_create(user=request.user, paper=paper)
    initial_index = progress.current_index if progress.current_index is not None else 0
    
    # Get user mistakes (IDs only) to highlight stars
    mistake_ids = list(UserMistake.objects.filter(user=request.user, question__paper=paper).values_list('question_id', flat=True))
    
    # Prepare questions data for JS
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.original_id,
            'db_id': q.id, # adding real DB ID for marking
            'type': q.q_type,
            'content': q.content,
            'answer': q.answer,
            'explanation': q.explanation,
            'options': q.options if q.options else []
        })

    # Pre-process questions for template rendering
    for q in questions:
        if q.q_type == 'fill_blank':
            # Split answer by common separators (comma, Chinese comma, spaces)
            import re
            # Split by comma (full/half width), semicolon (full/half width) or newline
            parts = re.split(r'[,，;；\n]+', q.answer)
            q.answer_parts = [p.strip() for p in parts if p.strip()]
        else:
            q.answer_parts = []

    return render(request, 'core/exam_detail.html', {
        'paper': paper,
        'questions': questions, 
        'questions_json': json.dumps(questions_data), 
        'initial_index': initial_index,
        'mistake_ids': mistake_ids
    })

@login_required
def paper_preview(request, paper_id):
    paper = get_object_or_404(ExamPaper, id=paper_id)
    questions = paper.question_set.all().order_by('original_id')
    
    import re
    for q in questions:
        if q.q_type == 'fill_blank':
            parts = re.split(r'[,，;；\n]+', q.answer)
            q.answer_parts = [p.strip() for p in parts if p.strip()]
            
    return render(request, 'core/paper_preview.html', {
        'paper': paper,
        'questions': questions
    })

@login_required
def mistake_list(request):
    mistakes = UserMistake.objects.filter(user=request.user).select_related('question', 'question__paper').order_by('-last_mistake_time')
    
    import re
    for m in mistakes:
        q = m.question
        if q.q_type == 'fill_blank':
             parts = re.split(r'[,，;；\n]+', q.answer)
             q.answer_parts = [p.strip() for p in parts if p.strip()]

    return render(request, 'core/mistake_list.html', {'mistakes': mistakes})

@login_required
@require_POST
def delete_paper(request, paper_id):
    paper = get_object_or_404(ExamPaper, id=paper_id)
    # Optional: Permission check. For now allow if owner matches or if user is superuser
    if paper.owner and paper.owner != request.user and not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'msg': 'Permission denied'}, status=403)
        
    paper.delete()
    return JsonResponse({'status': 'ok'})

# --- API Endpoints ---

@login_required
@require_POST
def sync_progress(request):
    """
    接收前端发送的进度，更新数据库
    Data: { paper_id: 1, index: 5 }
    """
    try:
        data = json.loads(request.body)
        paper_id = data.get('paper_id')
        index = data.get('index')
        
        # Parse logic to get ID from "paper_1" string if needed, but let's assume raw ID passed
        # Front end currently sends 'paper_1', need to fix frontend or parse here
        # Let's clean up frontend to send just ID.
        
        UserProgress.objects.update_or_create(
            user=request.user, paper_id=paper_id,
            defaults={'current_index': index}
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)

@login_required
@require_POST
def submit_answer(request):
    """
    提交答案，记录进度和错题
    Data: { paper_id: 1, index: 5, question_id: 10, is_correct: true/false }
    """
    try:
        data = json.loads(request.body)
        paper_id = data.get('paper_id')
        index = data.get('index')
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')
        
        # 1. Update Progress
        if paper_id and index is not None:
             UserProgress.objects.update_or_create(
                user=request.user, paper_id=paper_id,
                defaults={'current_index': index}
            )
             
        # 2. Record Mistake
        if question_id:
            question = get_object_or_404(Question, id=question_id)
            if is_correct is False:
                # Wrong answer: Create or update mistake
                mistake, created = UserMistake.objects.get_or_create(
                    user=request.user, 
                    question=question,
                )
                if not created:
                    mistake.mistake_count += 1
                mistake.save() # Updates last_mistake_time due to auto_now=True
            
            # Optional: Remove from mistake list if correct? 
            # For now, let's keep it manual or separate logic.
            
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)

@login_required
@require_POST
def toggle_mistake(request):
    """
    收藏/取消收藏错题
    Data: { question_id: 123 }
    """
    try:
        data = json.loads(request.body)
        q_id = data.get('question_id')
        
        question = get_object_or_404(Question, id=q_id)
        mistake, created = UserMistake.objects.get_or_create(user=request.user, question=question)
        
        if not created:
            # If already exists, toggle off (delete)
            mistake.delete()
            return JsonResponse({'status': 'removed'})
        else:
            return JsonResponse({'status': 'added'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)
