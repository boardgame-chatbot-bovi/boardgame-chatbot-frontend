from django.core.management.base import BaseCommand
from chatbot.models import GPTRuleQA, FinetuningRuleQA

class Command(BaseCommand):
    help = 'QA 데이터베이스에 샘플 데이터를 추가합니다'
    
    def handle(self, *args, **options):
        self.stdout.write('샘플 QA 데이터를 추가하는 중...')
        
        # GPT 룰 설명 샘플 데이터
        gpt_samples = [
            {
                'game_name': '카탄',
                'question': '카탄 게임의 기본 룰을 알려주세요',
                'answer': '카탄은 3-4명이 플레이하는 전략 보드게임입니다. 플레이어는 자원(나무, 벽돌, 양, 밀, 철)을 모아 정착지, 도시, 도로를 건설하여 점수를 얻습니다. 먼저 10점을 달성하는 플레이어가 승리합니다.'
            },
            {
                'game_name': '카탄',
                'question': '카탄에서 도적은 어떻게 작동하나요?',
                'answer': '주사위 결과가 7이 나오면 도적이 활성화됩니다. 1) 카드를 8장 이상 가진 플레이어는 절반을 버립니다. 2) 주사위를 굴린 플레이어가 도적을 다른 지형 타일로 이동시킵니다. 3) 그 지형에 인접한 상대 플레이어 중 한 명에게서 무작위로 카드 1장을 가져옵니다.'
            },
            {
                'game_name': '스플렌더',
                'question': '스플렌더 게임 룰을 설명해주세요',
                'answer': '스플렌더는 2-4명이 플레이하는 엔진 빌딩 게임입니다. 플레이어는 보석을 모아 카드를 구매하고, 구매한 카드는 영구적인 보석 할인을 제공합니다. 먼저 15점을 달성하는 플레이어가 승리합니다.'
            },
            {
                'game_name': '아줄',
                'question': '아줄 타일링 규칙을 알려주세요',
                'answer': '아줄에서는 매 라운드 공장 디스플레이에서 같은 색깔의 타일을 모두 가져와야 합니다. 가져온 타일은 패턴 라인에 놓고, 완성된 라인의 타일 1개만 벽에 놓을 수 있습니다. 벽에 놓지 못한 타일은 바닥 라인으로 가서 감점됩니다.'
            },
            {
                'game_name': '윙스팬',
                'question': '윙스팬의 엔진 시스템을 설명해주세요',
                'answer': '윙스팬에서는 새 카드를 서식지에 놓으면 그 열의 모든 새들이 오른쪽부터 순서대로 능력을 발동합니다. 같은 서식지에 더 많은 새를 놓을수록 더 강력한 엔진이 만들어집니다. 각 새의 능력은 음식 획득, 알 낳기, 카드 뽑기 등 다양합니다.'
            }
        ]
        
        # 파인튜닝 룰 설명 샘플 데이터 (더 전문적이고 상세한 설명)
        finetuning_samples = [
            {
                'game_name': '카탄',
                'question': '카탄에서 개발 카드 사용 시점과 제약 사항은?',
                'answer': '개발 카드는 구매한 턴에는 사용할 수 없습니다(기사 카드 제외). 승점 카드는 게임 종료 시에만 공개하며, 한 턴에 여러 장을 공개할 수 있습니다. 기사 카드는 구매 즉시 사용 가능하지만 한 턴에 1장만 사용 가능합니다. 독점과 풍년 카드는 언제든 사용 가능하지만 역시 한 턴에 1장씩만 사용할 수 있습니다.'
            },
            {
                'game_name': '카탄',
                'question': '항구 무역의 정확한 규칙과 우선순위는?',
                'answer': '항구 무역은 주사위 굴리기 전후 언제든 가능합니다. 일반 항구(3:1)는 같은 자원 3장을 원하는 자원 1장으로 교환하고, 전문 항구(2:1)는 해당 자원 2장을 원하는 자원 1장으로 교환합니다. 플레이어 간 무역과 달리 은행과의 무역에는 제한이 없으며, 여러 번 연속으로 거래할 수 있습니다.'
            },
            {
                'game_name': '스플렌더',
                'question': '스플렌더의 동시 15점 달성 시 승부 판정 규칙은?',
                'answer': '여러 플레이어가 같은 라운드에 15점 이상을 달성한 경우, 다음 순서로 승부를 판정합니다: 1) 더 높은 점수를 가진 플레이어, 2) 점수가 같다면 구매한 개발 카드 수가 적은 플레이어가 승리합니다. 이는 더 효율적으로 점수를 달성했다고 판단하기 때문입니다.'
            },
            {
                'game_name': '아줄',
                'question': '아줄에서 벽 완성 시 추가 점수 계산 방법은?',
                'answer': '벽에 타일을 놓을 때 점수는 연결된 타일의 개수로 계산됩니다. 가로와 세로 방향 모두 확인하여, 새로 놓은 타일과 연결된 모든 타일 개수만큼 점수를 얻습니다. 만약 가로 3개, 세로 2개에 연결되면 5점을 얻습니다. 게임 종료 시에는 완성된 가로줄 당 2점, 완성된 세로줄 당 7점, 같은 색깔 5개 완성 시 10점의 보너스를 추가로 얻습니다.'
            },
            {
                'game_name': '윙스팬',
                'question': '윙스팬에서 알 제한과 서식지별 특수 규칙은?',
                'answer': '각 새 카드에는 최대 알 수용 개수가 정해져 있으며, 이를 초과할 수 없습니다. 숲 서식지는 음식 획득, 초원은 알 낳기, 습지는 카드 뽑기에 특화되어 있습니다. 서식지별 보너스 카드는 해당 서식지의 새 개수에 따라 추가 점수를 제공하므로, 균형있는 배치보다는 집중 전략이 유리할 수 있습니다.'
            }
        ]
        
        # GPT 룰 QA 데이터 추가
        for sample in gpt_samples:
            gpt_qa, created = GPTRuleQA.objects.get_or_create(
                game_name=sample['game_name'],
                question=sample['question'],
                defaults={'answer': sample['answer']}
            )
            if created:
                self.stdout.write(f'GPT QA 추가: {gpt_qa.game_name} - {gpt_qa.question[:30]}...')
        
        # 파인튜닝 룰 QA 데이터 추가
        for sample in finetuning_samples:
            ft_qa, created = FinetuningRuleQA.objects.get_or_create(
                game_name=sample['game_name'],
                question=sample['question'],
                defaults={'answer': sample['answer']}
            )
            if created:
                self.stdout.write(f'파인튜닝 QA 추가: {ft_qa.game_name} - {ft_qa.question[:30]}...')
        
        self.stdout.write(
            self.style.SUCCESS('샘플 데이터 추가가 완료되었습니다!')
        )
