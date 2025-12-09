import re
import json
import os

def parse_exam_file(file_path):
    """
    解析试卷文件，返回题目列表。
    目前仅支持 .txt 文件，未来可扩展 .docx
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.txt':
        return parse_txt(file_path)
    else:
        # TODO: Add docx support
        print(f"Unsupported file format: {ext}")
        return []

def parse_txt(file_path):
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Last resort: try latin-1 or ignore errors
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

    # 正则匹配： "1. (单选题..." 或 "1. （单选题..."
    question_pattern = re.compile(r'(\d+)\.\s*[（(](.*?)[\)）]', re.MULTILINE)
    
    matches = list(question_pattern.finditer(content))
    questions = []
    
    for i, match in enumerate(matches):
        start_index = match.start()
        end_index = matches[i+1].start() if i + 1 < len(matches) else len(content)
        
        full_block = content[start_index:end_index].strip()
        
        q_id = match.group(1)
        q_meta = match.group(2)
        
        # 提取题型
        q_type = "unknown"
        if "单选题" in q_meta: q_type = "single_choice"
        elif "多选题" in q_meta: q_type = "multi_choice"
        elif "判断" in q_meta: q_type = "true_false"
        elif "简答" in q_meta: q_type = "essay"
        elif "填空" in q_meta: q_type = "fill_blank"

        # 提取分数 (e.g., "5.0 分")
        score = 0
        score_match = re.search(r'(\d+(\.\d+)?) 分', q_meta)
        if score_match:
            score = float(score_match.group(1))

        # 切割答案和解析
        ans_split = re.split(r'\n\s*答案：', full_block, 1)
        if len(ans_split) > 1:
            body_part = ans_split[0]
            rest_part = ans_split[1]
            
            expl_split = re.split(r'\n\s*解析：', rest_part, 1)
            answer_text = expl_split[0].strip()
            explanation_text = expl_split[1].strip() if len(expl_split) > 1 else ""
        else:
            body_part = full_block
            answer_text = ""
            explanation_text = ""

        # 提取选项
        lines = body_part.split('\n')
        question_text_lines = []
        options = []
        
        start_parsing_lines = lines[1:] # Skip first line
        option_pattern = re.compile(r'^\s*([A-Z])\s+(.*)')
        
        for line in start_parsing_lines:
            line = line.strip()
            if not line: continue
            
            opt_match = option_pattern.match(line)
            if (q_type in ['single_choice', 'multi_choice']) and opt_match:
                options.append({
                    "label": opt_match.group(1),
                    "content": opt_match.group(2)
                })
            else:
                if not options:
                    question_text_lines.append(line)

        questions.append({
            "original_id": int(q_id),
            "type": q_type,
            "content": "\n".join(question_text_lines),
            "options": options if options else None,
            "answer": answer_text,
            "explanation": explanation_text,
            "score": score
        })

    return questions
