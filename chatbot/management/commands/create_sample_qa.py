from django.core.management.base import BaseCommand
from chatbot.models import GPTRuleQA, FinetuningRuleQA
import random

class Command(BaseCommand):
    help = '게임 순위 테스트를 위한 샘플 QA 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='생성할 QA 데이터 개수 (기본값: 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # 샘플 게임 목록
        games = [
            '뱅!', '카탄', '스플렌더', '킹 오브 도쿄', '레지스탕스: 아발론',
            '디셉션: 홍콩의 살인', '원나잇 마피아', '코드네임', '아줄',
            '티켓 투 라이드', '판데믹', '윙스팬', '테라포밍 마스', '글룸헤이븐',
            '카르카손', '도미니언', '7 원더스', '푸에르토 리코', '아그리콜라'
        ]
        
        # 샘플 질문들
        sample_questions = [
            "게임 시작은 어떻게 하나요?",
            "턴 순서는 어떻게 정하나요?",
            "이 카드의 효과를 잘 모르겠어요",
            "승리 조건이 무엇인가요?",
            "특수 능력은 언제 사용할 수 있나요?",
            "게임 종료 조건을 알려주세요",
            "이 액션을 할 수 있는 조건이 뭔가요?",
            "몇 명이서 플레이할 수 있나요?",
            "플레이 시간은 얼마나 걸리나요?",
            "초보자도 쉽게 할 수 있나요?",
            "이 규칙이 헷갈려요",
            "예외 상황은 어떻게 처리하나요?",
            "카드를 몇 장 뽑나요?",
            "리소스는 어떻게 관리하나요?",
            "공격은 어떻게 하나요?"
        ]
        
        # 샘플 답변들
        sample_answers = [
            "네, 그 규칙에 대해 설명드리겠습니다...",
            "해당 상황에서는 다음과 같이 진행하시면 됩니다...",
            "좋은 질문입니다! 그 부분은...",
            "규칙서에 따르면 다음과 같습니다...",
            "그 경우에는 특별 규칙이 적용됩니다...",
            "초보자분들이 자주 궁금해하시는 부분이네요...",
            "단계별로 설명드리면...",
            "예외 상황이므로 이렇게 처리하시면 됩니다...",
            "카드 효과는 다음과 같이 작동합니다...",
            "게임의 핵심 메커니즘은..."
        ]
        
        created_gpt = 0
        created_ft = 0
        
        # GPT QA 데이터 생성
        for i in range(count // 2):
            game = random.choice(games)
            question = random.choice(sample_questions)
            answer = random.choice(sample_answers)
            
            GPTRuleQA.objects.create(
                game_name=game,
                question=f"{question} ({game} 관련)",
                answer=f"{answer} {game}에서는 이렇게 진행됩니다."
            )
            created_gpt += 1
        
        # 파인튜닝 QA 데이터 생성 (뱅! 게임에 더 많이 할당)
        for i in range(count // 2):
            if i < (count // 4):  # 절반은 뱅! 게임으로
                game = '뱅!'
            else:
                game = random.choice(games)
                
            question = random.choice(sample_questions)
            answer = random.choice(sample_answers)
            
            FinetuningRuleQA.objects.create(
                game_name=game,
                question=f"{question} ({game} 전문 질문)",
                answer=f"{answer} 파인튜닝된 AI가 정확히 답변드립니다."
            )
            created_ft += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'성공적으로 샘플 데이터를 생성했습니다!\n'
                f'GPT QA: {created_gpt}개\n'
                f'파인튜닝 QA: {created_ft}개\n'
                f'총 {created_gpt + created_ft}개의 QA 데이터가 생성되었습니다.'
            )
        )
