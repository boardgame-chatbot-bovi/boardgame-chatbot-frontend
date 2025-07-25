from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import qrcode
import io
import logging
import requests
from .models import GPTRuleQA, FinetuningRuleQA, get_combined_game_rankings
from .services.game_recommendation import GameRecommendationService
from .services.rule_explanation import RuleExplanationService

logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성 (싱글톤 패턴)
game_recommendation_service = GameRecommendationService()
rule_explanation_service = RuleExplanationService()



def home(request):
    """홈페이지"""
    # 서비스 상태 체크
    try:
        rec_status = game_recommendation_service.get_service_status()
        rule_status = rule_explanation_service.get_service_status()
        
        # 게임 순위 데이터 가져오기
        game_rankings = get_combined_game_rankings(limit=10)
        
        context = {
            'recommendation_status': rec_status.get('status', 'unknown'),
            'rule_status': rule_status.get('status', 'unknown'),
            'game_rankings': game_rankings
        }
    except Exception as e:
        logger.error(f"❌ 서비스 상태 확인 실패: {str(e)}")
        context = {
            'recommendation_status': 'error',
            'rule_status': 'error',
            'game_rankings': []
        }
    
    return render(request, 'chatbot/home.html', context)

def game_recommendation(request):
    """게임 추천 페이지"""
    return render(request, 'chatbot/game_recommendation.html')

def gpt_rules(request):
    """GPT 룰 설명 페이지"""
    available_games = rule_explanation_service.get_available_games()
    context = {'available_games': available_games}
    return render(request, 'chatbot/gpt_rules.html', context)

def finetuning_rules(request):
    """파인튜닝 룰 설명 페이지"""
    available_games = rule_explanation_service.get_available_games()
    context = {'available_games': available_games}
    return render(request, 'chatbot/finetuning_rules.html', context)

def mobile_chat(request, chat_type):
    """모바일 채팅 페이지"""
    chat_type_names = {
        'gpt_rules': 'GPT 룰 설명',
        'finetuning_rules': '파인튜닝 룰 설명'
    }
    
    available_games = rule_explanation_service.get_available_games()
    
    context = {
        'chat_type': chat_type,
        'chat_type_name': chat_type_names.get(chat_type, '채팅'),
        'available_games': available_games
    }
    return render(request, 'chatbot/mobile_chat.html', context)

@csrf_exempt
def chat_api(request):
    """🔥 핵심: 채팅 API - Runpod 백엔드 연동"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            chat_type = data.get('chat_type', '')
            game_name = data.get('game_name', '')
            session_id = data.get('session_id', '')  # 세션 ID 받기
            
            logger.info(f"💬 채팅 요청: {chat_type} - {message} (세션: {session_id})")
            
            # 세션 초기화 더미 요청 처리
            if message == '__INIT_SESSION__':
                logger.info(f"🚀 세션 초기화 요청")
                # 빈 session_id로 더미 요청을 보내서 세션 ID만 받아오기
                result = game_recommendation_service.recommend_games("initialize", session_id)
                
                if isinstance(result, dict):
                    response_data = {
                        'response': "세션이 초기화되었습니다.",  # 더미 메시지
                        'session_id': result.get('session_id', session_id)
                    }
                else:
                    response_data = {
                        'response': "세션이 초기화되었습니다.",
                        'session_id': session_id
                    }
                    
                logger.info(f"✅ 세션 초기화 완료: {response_data.get('session_id')}")
                
                # 세션 초기화 응답 바로 리턴
                return JsonResponse({
                    'response': response_data.get('response'),
                    'session_id': response_data.get('session_id'),
                    'status': 'success'
                })
            
            # 채팅 타입에 따라 다른 응답
            response_data = None
            
            if chat_type == 'game_recommendation':
                # 게임 추천 서비스 호출
                result = game_recommendation_service.recommend_games(message, session_id)
                logger.info(f"🔍 게임 추천 서비스 반환 데이터: {result}")
                
                # RunPod 클라이언트에서 딕셔너리 형태로 반환하는 경우
                if isinstance(result, dict):
                    response_data = {
                        'response': result.get('response', ''),
                        'session_id': result.get('session_id', session_id)
                    }
                    logger.info(f"🔍 세션 ID 추출: {result.get('session_id', session_id)}")
                else:
                    # 문자열로 반환하는 경우 (폴백 등)
                    response_data = {
                        'response': result,
                        'session_id': session_id
                    }
                    logger.warning(f"⚠️ 게임 추천 서비스가 문자열로 반환함: {type(result)}")
                
            elif chat_type in ['gpt_rules', 'finetuning_rules']:
                if not game_name:
                    response_data = {
                        'response': "게임을 먼저 선택해주세요.",
                        'session_id': session_id
                    }
                else:
                    # 파인튜닝 타입 매핑
                    api_chat_type = "finetuning" if chat_type == 'finetuning_rules' else "gpt"
                    result = rule_explanation_service.answer_rule_question(
                        game_name, message, api_chat_type, session_id
                    )
                    logger.info(f"🔍 룰 설명 서비스 반환 데이터: {result}")
                    
                    # 서비스에서 딕셔너리 형태로 반환하는 경우
                    if isinstance(result, dict):
                        response_data = {
                            'response': result.get('response', ''),
                            'session_id': result.get('session_id', session_id)
                        }
                        response_text = result.get('response', '')
                    else:
                        # 문자열로 반환하는 경우 (하위 호환성)
                        response_data = {
                            'response': result,
                            'session_id': session_id
                        }
                        response_text = result
                        logger.warning(f"⚠️ 룰 설명 서비스가 문자열로 반환함: {type(result)}")
                    
                    # 🔥 핵심: 질문과 답변을 QA DB에 자동 저장!
                    try:
                        if chat_type == 'gpt_rules':
                            GPTRuleQA.objects.create(
                                game_name=game_name,
                                question=message,
                                answer=response_text
                            )
                            logger.info(f"✅ GPT QA 저장: {game_name} - {message[:30]}...")
                            
                        elif chat_type == 'finetuning_rules':
                            FinetuningRuleQA.objects.create(
                                game_name=game_name,
                                question=message,
                                answer=response_text
                            )
                            logger.info(f"✅ 파인튜닝 QA 저장: {game_name} - {message[:30]}...")
                    except Exception as e:
                        logger.error(f"❌ QA 저장 실패: {str(e)}")
            else:
                response_data = {'response': "알 수 없는 채팅 타입입니다."}
            
            # 응답 데이터 처리
            if isinstance(response_data, dict):
                # 서비스에서 session_id가 포함된 딕셔너리를 반환한 경우
                result = {
                    'response': response_data.get('response', ''),
                    'session_id': response_data.get('session_id', session_id),
                    'status': 'success'
                }
            else:
                # 서비스에서 문자열만 반환한 경우
                result = {
                    'response': response_data,
                    'session_id': session_id,
                    'status': 'success'
                }
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"❌ 채팅 API 오류: {str(e)}")
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

@csrf_exempt
def close_session_api(request):
    """세션 종료 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id', '')
            
            if not session_id:
                return JsonResponse({'error': '세션 ID가 필요합니다.'}, status=400)
            
            logger.info(f"🗑️ 세션 종료 요청: {session_id}")
            
            # 게임 추천 서비스에 세션 종료 요청
            rec_success = game_recommendation_service.close_session(session_id)
            
            # 룰 설명 서비스에 세션 종료 요청
            rule_success = rule_explanation_service.close_session(session_id)
            
            # 두 서비스 중 하나라도 성공하면 성공으로 처리
            success = rec_success or rule_success
            
            return JsonResponse({
                'status': 'success' if success else 'warning',
                'message': f'세션 {session_id} 종료 완료' if success else f'세션 {session_id}를 찾을 수 없습니다.',
                'details': {
                    'recommendation_service': rec_success,
                    'rule_service': rule_success
                }
            })
            
        except Exception as e:
            logger.error(f"❌ 세션 종료 API 오류: {str(e)}")
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

@csrf_exempt
def rule_summary_api(request):
    """게임 룰 요약 API - Runpod 백엔드 연동"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            game_name = data.get('game_name', '')
            chat_type = data.get('chat_type', 'gpt_rules')
            session_id = data.get('session_id', '')
            
            if not game_name:
                return JsonResponse({'error': '게임 이름이 필요합니다.'}, status=400)
            
            logger.info(f"📖 룰 요약 요청: {game_name} ({chat_type}, 세션: {session_id})")
            
            # 파인튜닝 타입 매핑
            api_chat_type = "finetuning" if chat_type == 'finetuning_rules' else "gpt"
            result = rule_explanation_service.explain_game_rules(game_name, api_chat_type, session_id)
            
            logger.info(f"🔍 룰 요약 서비스 반환 데이터: {result}")
            
            # 서비스에서 딕셔너리 형태로 반환하는 경우
            if isinstance(result, dict):
                return JsonResponse({
                    'summary': result.get('response', ''),
                    'game_name': game_name,
                    'session_id': result.get('session_id', session_id),
                    'status': 'success'
                })
            else:
                # 문자열로 반환하는 경우 (하위 호환성)
                return JsonResponse({
                    'summary': result,
                    'game_name': game_name,
                    'session_id': session_id,
                    'status': 'success'
                })
            
        except Exception as e:
            logger.error(f"❌ 룰 요약 API 오류: {str(e)}")
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=400)
    
    return JsonResponse({'error': 'POST method required'}, status=405)

def generate_qr(request, chat_type):
    """QR 코드 생성 - urllib로 IP 감지"""
    import os
    import urllib.request
    import urllib.error
    
    # 1순위: 환경변수로 QR_BASE_URL이 설정된 경우
    qr_base_url = os.getenv('QR_BASE_URL')
    
    if qr_base_url:
        mobile_url = f"{qr_base_url.rstrip('/')}{reverse('chatbot:mobile_chat', args=[chat_type])}"
        logger.info(f"📱 QR 코드 생성 (환경변수): {mobile_url}")
    else:
        # 2순위: urllib로 직접 IP 가져오기
        public_ip = None
        
        # 외부 IP 서비스들 순차적으로 시도
        ip_services = [
            'https://ifconfig.me/ip',
            'https://icanhazip.com',
            'https://ipecho.net/plain',
            'https://api.ipify.org',
            'https://checkip.amazonaws.com'
        ]
        
        for service in ip_services:
            try:
                with urllib.request.urlopen(service, timeout=5) as response:
                    ip = response.read().decode('utf-8').strip()
                    if ip and '.' in ip and not ip.startswith('127.'):
                        public_ip = ip
                        service_name = service.split('/')[-2] if service.endswith('/') else service.split('/')[-1]
                        logger.info(f"📱 IP 감지 성공 ({service_name}): {public_ip}")
                        break
            except Exception as e:
                logger.debug(f"📱 IP 감지 실패 ({service}): {str(e)}")
                continue
        
        # IP를 찾았으면 QR URL 생성
        if public_ip:
            mobile_url = f"http://{public_ip}{reverse('chatbot:mobile_chat', args=[chat_type])}"
            logger.info(f"📱 QR 코드 생성 (자동 IP: {public_ip}): {mobile_url}")
        else:
            # 3순위: request.get_host() 사용 (폴백)
            host = request.get_host()
            if request.is_secure():
                base_url = f"https://{host}"
            else:
                base_url = f"http://{host}"
            mobile_url = f"{base_url}{reverse('chatbot:mobile_chat', args=[chat_type])}"
            logger.warning(f"📱 QR 코드 생성 (폴백 - IP 감지 실패): {mobile_url}")
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(mobile_url)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    qr_image.save(buffer, format='PNG')
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def qa_stats(request):
    """QA 데이터 통계"""
    gpt_count = GPTRuleQA.objects.count()
    ft_count = FinetuningRuleQA.objects.count()
    recent_gpt = GPTRuleQA.objects.all()[:10]
    recent_ft = FinetuningRuleQA.objects.all()[:10]
    
    context = {
        'gpt_count': gpt_count,
        'ft_count': ft_count,
        'total_count': gpt_count + ft_count,
        'recent_gpt': recent_gpt,
        'recent_ft': recent_ft,
    }
    
    return render(request, 'chatbot/qa_stats.html', context)
