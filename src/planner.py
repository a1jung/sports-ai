# src/planner.py
from typing import Dict, Any
from src.kb.knowledge_loader import load_all_knowledge
from src.ai.ai_client import ask_openai

# Load knowledge base at import
KB = load_all_knowledge()

def ensure_minimum_lists(plan: Dict[str, Any]) -> None:
    """
    최소 3개의 전문 훈련 방법과 1개의 주의사항 확보
    """
    while len(plan.get('professional_methods', [])) < 3:
        plan.setdefault('professional_methods', []).append(
            '기본 전문 훈련: 기술 반복 + 비디오 분석 + 체력 훈련'
        )
    if not plan.get('precautions'):
        plan['precautions'] = [
            '훈련 전 충분한 워밍업',
            '통증 시 즉시 중단',
            '전문가 상담 권장'
        ]

def generate_plan(
    sport: str, goal: str, level: str, premium: bool = False
) -> Dict[str, Any]:
    """
    스포츠별 맞춤 훈련 계획 생성
    """
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

    # KB 활용
    kb = KB.get(sport)
    if kb:
        overview = None
        if isinstance(kb, dict):
            if 'overview' in kb:
                overview = kb.get('overview')
            elif 'description' in kb:
                overview = kb.get('description')
            else:
                for subk, subv in kb.items():
                    if isinstance(subv, dict) and 'description' in subv:
                        overview = subv.get('description')
                        break
        plan['summary'] = overview or f'{sport} 맞춤 훈련 계획입니다.'

        # 전문 훈련 방법
        training = []
        if isinstance(kb, dict):
            for key in ['training', 'training_methods', 'methods', 'on_water_training']:
                if key in kb:
                    training = kb.get(key) if isinstance(kb.get(key), list) else [kb.get(key)]
                    break
            if not training:
                for sub in kb.values():
                    if isinstance(sub, dict):
                        for key in ['training', 'on_water_training', 'methods']:
                            if key in sub:
                                training = sub.get(key) if isinstance(sub.get(key), list) else [sub.get(key)]
                                break
                    if training:
                        break
        if training:
            plan['professional_methods'] = [str(x) for x in training][:10]

        # 주의사항
        tips = []
        if isinstance(kb, dict):
            for key in ['tips', 'warnings', 'precautions']:
                if key in kb:
                    tips = kb.get(key) if isinstance(kb.get(key), list) else [kb.get(key)]
                    break
            if not tips:
                for sub in kb.values():
                    if isinstance(sub, dict):
                        for key in ['tips', 'warnings', 'precautions']:
                            if key in sub:
                                tips = sub.get(key) if isinstance(sub.get(key), list) else [sub.get(key)]
                                break
                    if tips:
                        break
        if tips:
            plan['precautions'] = [str(x) for x in tips][:10]
    else:
        plan['summary'] = f"No local KB for {sport}. Generating generic plan."

    # 최소 훈련/주의사항 확보
    ensure_minimum_lists(plan)

    # 주간 계획 예시
    lvl = level.lower() if level else ''
    if lvl.startswith('beg'):
        plan['weekly_plan'] = [
            {'day': 'Mon', 'session': '기본 기술 & 워밍업 - 30~40분'},
            {'day': 'Wed', 'session': '기초 체력(근력/유연성) - 30분'},
            {'day': 'Sat', 'session': '실전 형태 연습(저강도) - 40분'}
        ]
    elif lvl.startswith('adv'):
        plan['weekly_plan'] = [
            {'day': 'Mon', 'session': '기술 세션(고강도) - 60분'},
            {'day': 'Tue', 'session': '영상분석 + 개인 보강 - 45분'},
            {'day': 'Thu', 'session': '인터벌/체력 - 50분'},
            {'day': 'Sat', 'session': '매치 시뮬레이션 - 70~90분'}
        ]
    else:
        plan['weekly_plan'] = [
            {'day': 'Mon', 'session': '기술 연습 - 45분'},
            {'day': 'Wed', 'session': '체력/밸런스 - 40분'},
            {'day': 'Fri', 'session': '전술/실전 연습 - 60분'}
        ]

    # 프리미엄 기능: OpenAI 기반 강화
    if premium:
        prompt = (
            f"You are an expert {sport} coach. "
            f"User goal: {goal}. "
            f"Current level: {level}. "
            "Provide 3 advanced training drills with short explanations and 1-week progressive microcycle."
        )
        ai_text = ask_openai(prompt)
        plan['ai_enhancement'] = ai_text

    return plan
