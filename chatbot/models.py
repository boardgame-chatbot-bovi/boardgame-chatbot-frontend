from django.db import models
from django.db.models import Count

# Create your models here.
class GPTRuleQA(models.Model):
    """GPT 룰 설명 질문답변 - 사용자가 질문하면 자동 저장"""
    # 번호 (PK, 오토인크리먼트) - Django가 자동으로 id 필드 생성
    game_name = models.CharField('게임 이름', max_length=100)
    question = models.TextField('질문 내용')
    answer = models.TextField('답변 내용')
    created_at = models.DateTimeField('생성 시간', auto_now_add=True)
    
    class Meta:
        verbose_name = 'GPT 룰 QA'
        verbose_name_plural = 'GPT 룰 QA들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.id}: {self.game_name} - {self.question[:30]}"
    
    @classmethod
    def get_game_rankings(cls, limit=10):
        """게임별 질문 수 순위를 반환"""
        return cls.objects.values('game_name').annotate(
            question_count=Count('id')
        ).order_by('-question_count')[:limit]


class FinetuningRuleQA(models.Model):
    """파인튜닝 룰 설명 질문답변 - 사용자가 질문하면 자동 저장"""
    # 번호 (PK, 오토인크리먼트) - Django가 자동으로 id 필드 생성
    game_name = models.CharField('게임 이름', max_length=100)
    question = models.TextField('질문 내용')
    answer = models.TextField('답변 내용')
    created_at = models.DateTimeField('생성 시간', auto_now_add=True)
    
    class Meta:
        verbose_name = '파인튜닝 룰 QA'
        verbose_name_plural = '파인튜닝 룰 QA들'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.id}: {self.game_name} - {self.question[:30]}"
    
    @classmethod
    def get_game_rankings(cls, limit=10):
        """게임별 질문 수 순위를 반환"""
        return cls.objects.values('game_name').annotate(
            question_count=Count('id')
        ).order_by('-question_count')[:limit]


# 통합 게임 순위 조회 함수
def get_combined_game_rankings(limit=10):
    """GPT와 파인튜닝 QA를 합쳐서 게임별 질문 수 순위를 반환"""
    from django.db.models import Value
    from django.db.models.functions import Coalesce
    
    # GPT QA에서 게임별 질문 수
    gpt_rankings = GPTRuleQA.objects.values('game_name').annotate(
        gpt_count=Count('id')
    )
    
    # 파인튜닝 QA에서 게임별 질문 수  
    ft_rankings = FinetuningRuleQA.objects.values('game_name').annotate(
        ft_count=Count('id')
    )
    
    # 모든 게임 이름 수집
    all_games = set()
    gpt_data = {item['game_name']: item['gpt_count'] for item in gpt_rankings}
    ft_data = {item['game_name']: item['ft_count'] for item in ft_rankings}
    
    all_games.update(gpt_data.keys())
    all_games.update(ft_data.keys())
    
    # 통합 순위 계산
    combined_rankings = []
    for game in all_games:
        gpt_count = gpt_data.get(game, 0)
        ft_count = ft_data.get(game, 0)
        total_count = gpt_count + ft_count
        
        combined_rankings.append({
            'game_name': game,
            'total_count': total_count,
            'gpt_count': gpt_count,
            'ft_count': ft_count
        })
    
    # 총 질문 수로 정렬
    combined_rankings.sort(key=lambda x: x['total_count'], reverse=True)
    
    return combined_rankings[:limit]
