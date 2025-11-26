# src/planner.py
from typing import Dict, Any
from src.kb.knowledge_loader import load_all_knowledge
from src.ai.ai_client import ask_openai

KB = load_all_knowledge()

def ensure_minimum_lists(plan: Dict[str, Any]) -> None:
    # ensure at least 3 professional methods and at least 1 precaution
    while len(plan.get('professional_methods', [])) < 3:
        plan.setdefault('professional_methods', []).append('기본 전문 훈련: 기술 반복 + 비디오 분석 + 체력 훈련')
    if not plan.get('precautions'):
        plan['precautions'] = ['훈련 전 충분한 워밍업', '통증 시 즉시 중단', '전문가 상담 권장']

def generate_plan(sport: str, goal: str, level: str, premium: bool = False) -> Dict[str, Any]:
    sport = sport or ''
    plan = {
        'sport': sport,
        'goal': goal,
        'level': level,
        'summary': '',
        'professional_methods': [],
        'precautions': [],
        'weekly_plan': []
    }

    # Try to use KB
    kb = KB.get(sport)
    if kb:
        # try to extract overview/description
        overview = None
        # kb may be nested (e.g., yacht -> 470 -> description) or flat
        if isinstance(kb, dict):
            # pick top-level 'overview' or 'description' if present
            if 'overview' in kb:
                overview = kb.get('overview')
            elif 'description' in kb:
                overview = kb.get('description')
            else:
                # if nested categories (like 470), try to take first nested description
                for subk, subv in kb.items():
                    if isinstance(subv, dict):
                        if 'description' in subv:
                            overview = subv.get('description')
                            break
        plan['summary'] = overview or f'{sport} 맞춤 훈련 계획입니다.'

        # professional methods
        training = []
        # attempt common keys
        if isinstance(kb, dict):
            for key in ['training','training_methods','methods','on_water_training']:
                if key in kb:
                    training = kb.get(key) if isinstance(kb.get(key), list) else [kb.get(key)]
                    break
            # scan nested subfolders
            if not training:
                for sub in kb.values():
                    if isinstance(sub, dict):
                        for key in ['training','on_water_training','methods']:
                            if key in sub:
                                training = sub.get(key) if isinstance(sub.get(key), list) else [sub.get(key)]
                                break
                    if training:
                        break
        if training:
            plan['professional_methods'] = [str(x) for x in training][:10]

        # precautions/tips
        tips = []
        if isinstance(kb, dict):
            for key in ['tips','warnings','precautions']:
                if key in kb:
                    tips = kb.get(key) if isinstance(kb.get(key), list) else [kb.get(key)]
                    break
            if not tips:
                for sub in kb.values():
                    if isinstance(sub, dict):
                        for key in ['tips','warnings','precautions']:
                            if key in sub:
                                tips = sub.get(key) if isinstance(sub.get(key), list) else [sub.get(key)]
                                break
                    if tips:
                        break
        if tips:
            plan['precautions'] = [str(x) for x in tips][:10]
    else:
        plan['summary'] = f"No local KB for {sport}. Generating generic plan."

    # ensure minimums
    ensure_minimum_lists(plan)

    # sample weekly plan depending on level
    if level and level.lower().startswith('beg'):
        plan['weekly_plan'] = [
            {'day':'Mon','session':'기본 기술 & 워밍업 - 30~40분'},
            {'day':'Wed','session':'기초 체력(근력/유연성) - 30분'},
            {'day':'Sat','session':'실전 형태 연습(저강도) - 40분'}
        ]
    elif level and level.lower().startswith('adv'):
        plan['weekly_plan'] = [
            {'day':'Mon','session':'기술 세션(고강도) - 60분'},
            {'day':'Tue','session':'영상분석 + 개인 보강 - 45분'},
            {'day':'Thu','session':'인터벌/체력 - 50분'},
            {'day':'Sat','session':'매치 시뮬레이션 - 70~90분'}
        ]
    else:
        plan['weekly_plan'] = [
            {'day':'Mon','session':'기술 연습 - 45분'},
            {'day':'Wed','session':'체력/밸런스 - 40분'},
            {'day':'Fri','session':'전술/실전 연습 - 60분'}
        ]

    # premium enhancement via OpenAI (if requested)
    if premium:
        prompt = f\"You are an expert {sport} coach. User goal: {goal}. Current level: {level}. Provide 3 advanced training drills with short explanations and 1-week progressive microcycle.\"
        ai_text = ask_openai(prompt)
        plan['ai_enhancement'] = ai_text

    return plan
