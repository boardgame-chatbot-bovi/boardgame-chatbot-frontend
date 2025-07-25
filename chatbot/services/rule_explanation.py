import logging
from django.conf import settings
from .runpod_client import RunpodClient

logger = logging.getLogger(__name__)

class RuleExplanationService:
    """룰 설명 서비스 - Runpod 백엔드 연동 (GPT/파인튜닝 세션 분리)"""
    
    def __init__(self):
        # Runpod 클라이언트 초기화
        self.runpod_client = RunpodClient()
        
        # 폴백 옵션 설정
        self.use_fallback = getattr(settings, 'RUNPOD_USE_FALLBACK', True)
        
        # 게임 목록 가져오기 (캐시용)
        self._available_games = None
        
        logger.info("✅ 룰 설명 서비스가 초기화되었습니다.")
    
    def get_available_games(self):
        """사용 가능한 게임 목록 반환 (캐싱)"""
        if self._available_games is None:
            try:
                self._available_games = self.runpod_client.sync_get_available_games()
                logger.info(f"✅ 게임 목록 로드: {len(self._available_games)}개")
            except Exception as e:
                logger.error(f"❌ 게임 목록 로드 실패: {str(e)}")
                # 기본 게임 목록
                self._available_games = [
                    "카탄", "스플렌더", "아줄", "윙스팬", "뱅", 
                    "킹 오브 도쿄", "7 원더스", "도미니언", "스몰 월드", "티켓 투 라이드"
                ]
        
        return self._available_games
    
    def explain_game_rules(self, game_name, chat_type='gpt_rules', session_id=""):
        """게임 룰 전체 설명 (GPT 또는 파인튜닝 세션 관리 포함)"""
        session_type = 'gpt' if chat_type == 'gpt_rules' else 'finetuning'
        
        if game_name not in self.get_available_games():
            return {
                'response': f"'{game_name}' 게임은 현재 지원하지 않습니다.",
                'session_id': session_id,
                'session_type': session_type
            }
        
        try:
            logger.info(f"📚 룰 요약 요청: {game_name} ({session_type} 세션: {session_id})")
            result = self.runpod_client.sync_rule_summary(game_name, chat_type, session_id)
            
            # 세션 ID 처리: 백엔드에서 받은 session_id 사용
            actual_session_id = result.get('session_id', session_id)
            actual_session_type = result.get('session_type', session_type)
            
            logger.info(f"✅ 룰 요약 완료 ({actual_session_type} 세션: {actual_session_id})")
            
            return {
                'response': result.get('response', '요약을 가져올 수 없습니다.'),
                'session_id': actual_session_id,
                'session_type': actual_session_type
            }
            
        except Exception as e:
            logger.error(f"❌ 룰 설명 실패 ({session_type}): {str(e)}")
            
            if self.use_fallback:
                fallback_response = self._get_fallback_rule_explanation(game_name, chat_type)
                return {
                    'response': fallback_response,
                    'session_id': session_id,
                    'session_type': session_type
                }
            else:
                return {
                    'response': f"룰 설명 서비스에 일시적인 문제가 발생했습니다: {str(e)}",
                    'session_id': session_id,
                    'session_type': session_type
                }
    
    def answer_rule_question(self, game_name, question, chat_type='gpt_rules', session_id=""):
        """특정 룰 질문에 답변 (GPT 또는 파인튜닝 세션 관리 포함)"""
        session_type = 'gpt' if chat_type == 'gpt_rules' else 'finetuning'
        
        if game_name not in self.get_available_games():
            return {
                'response': f"'{game_name}' 게임은 현재 지원하지 않습니다.",
                'session_id': session_id,
                'session_type': session_type
            }
        
        try:
            logger.info(f"💬 룰 질문: {game_name} - {question} ({session_type} 세션: {session_id})")
            result = self.runpod_client.sync_explain_rules(game_name, question, chat_type, session_id)
            
            # 세션 ID 처리: 백엔드에서 받은 session_id 사용
            actual_session_id = result.get('session_id', session_id)
            actual_session_type = result.get('session_type', session_type)
            
            logger.info(f"✅ 룰 질문 답변 완료 ({actual_session_type} 세션: {actual_session_id})")
            
            return {
                'response': result.get('response', '답변을 가져올 수 없습니다.'),
                'session_id': actual_session_id,
                'session_type': actual_session_type
            }
            
        except Exception as e:
            logger.error(f"❌ 룰 질문 답변 실패 ({session_type}): {str(e)}")
            
            if self.use_fallback:
                fallback_response = self._get_fallback_rule_answer(game_name, question, chat_type)
                return {
                    'response': fallback_response,
                    'session_id': session_id,
                    'session_type': session_type
                }
            else:
                return {
                    'response': f"룰 질문 답변 서비스에 일시적인 문제가 발생했습니다: {str(e)}",
                    'session_id': session_id,
                    'session_type': session_type
                }
    
    def close_session(self, session_id, session_type=None):
        """세션 종료 요청 (GPT 또는 파인튜닝 세션)"""
        try:
            session_info = f" ({session_type})" if session_type else ""
            logger.info(f"🗑️ 룰 설명 세션 종료 요청{session_info}: {session_id}")
            result = self.runpod_client.sync_close_session(session_id)
            return result.get('success', False) if isinstance(result, dict) else True
        except Exception as e:
            session_info = f" ({session_type})" if session_type else ""
            logger.error(f"❌ 룰 설명 세션 종료 실패{session_info}: {str(e)}")
            return False
    
    def _get_fallback_rule_explanation(self, game_name, chat_type):
        """폴백 룰 설명 (Runpod 서버 다운 시)"""
        fallback_rules = {
            "카탄": "카탄은 자원을 수집하여 도로와 건물을 건설하는 전략 게임입니다. 주사위를 굴려 자원을 획득하고, 다른 플레이어와 거래할 수 있습니다.",
            "스플렌더": "스플렌더는 보석 카드를 수집하여 점수를 얻는 게임입니다. 토큰을 사용해 카드를 구매하고, 카드의 보너스로 더 비싼 카드를 살 수 있습니다.",
            "뱅": "뱅은 서부 테마의 숨겨진 역할 게임입니다. 보안관, 부관, 무법자, 배신자 중 하나의 역할을 맡아 각자의 목표를 달성해야 합니다.",
            "아줄": "아줄은 타일을 배치하여 아름다운 패턴을 만드는 게임입니다. 타일을 선택하고 배치하여 점수를 얻되, 벌점을 피해야 합니다."
        }
        
        rule = fallback_rules.get(game_name, f"{game_name}은 흥미로운 보드게임입니다. 정확한 룰은 게임 설명서를 참조해주세요.")
        
        prefix = "🤖 기본 설명 (AI 서버 연결 불가)" if chat_type == 'gpt_rules' else "⚙️ 기본 설명 (AI 서버 연결 불가)"
        return f"{prefix}:\n\n{rule}"
    
    def _get_fallback_rule_answer(self, game_name, question, chat_type):
        """폴백 룰 질문 답변 (Runpod 서버 다운 시)"""
        fallback_answers = {
            "몇 명": f"{game_name}은 일반적으로 2-4명이 플레이할 수 있습니다.",
            "시간": f"{game_name}은 보통 30-60분 정도 소요됩니다.",
            "난이도": f"{game_name}은 중간 난이도의 게임입니다.",
            "나이": f"{game_name}은 10세 이상부터 플레이 가능합니다."
        }
        
        # 키워드 매칭으로 기본 답변 제공
        for keyword, answer in fallback_answers.items():
            if keyword in question:
                prefix = "🤖 기본 답변 (AI 서버 연결 불가)" if chat_type == 'gpt_rules' else "⚙️ 기본 답변 (AI 서버 연결 불가)"
                return f"{prefix}:\n\n{answer}"
        
        # 기본 답변
        prefix = "🤖 기본 답변 (AI 서버 연결 불가)" if chat_type == 'gpt_rules' else "⚙️ 기본 답변 (AI 서버 연결 불가)"
        return f"{prefix}:\n\n{game_name}에 대한 구체적인 답변을 제공하지 못해 죄송합니다. 게임 설명서를 확인하시거나 나중에 다시 시도해주세요."
    
    def get_service_status(self):
        """서비스 상태 확인"""
        try:
            health = self.runpod_client.sync_health_check()
            return {
                "status": "healthy" if health.get("status") == "healthy" else "degraded",
                "backend": "runpod",
                "details": health,
                "langchain_enabled": True,
                "session_management": "separated"  # GPT와 파인튜닝 세션 분리됨
            }
        except Exception as e:
            return {
                "status": "error",
                "backend": "runpod",
                "error": str(e),
                "langchain_enabled": True,
                "session_management": "separated"  # GPT와 파인튜닝 세션 분리됨
            }
