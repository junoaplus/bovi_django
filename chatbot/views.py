from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import qrcode
import io
import logging
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
            
            logger.info(f"💬 채팅 요청: {chat_type} - {message}")
            
            # 채팅 타입에 따라 다른 응답
            if chat_type == 'game_recommendation':
                response = game_recommendation_service.recommend_games(message)
                
            elif chat_type in ['gpt_rules', 'finetuning_rules']:
                if not game_name:
                    response = "게임을 먼저 선택해주세요."
                else:
                    # 파인튜닝 타입 매핑
                    api_chat_type = "finetuning" if chat_type == 'finetuning_rules' else "gpt"
                    response = rule_explanation_service.answer_rule_question(
                        game_name, message, api_chat_type
                    )
                    
                    # 🔥 핵심: 질문과 답변을 QA DB에 자동 저장!
                    try:
                        if chat_type == 'gpt_rules':
                            GPTRuleQA.objects.create(
                                game_name=game_name,
                                question=message,
                                answer=response
                            )
                            logger.info(f"✅ GPT QA 저장: {game_name} - {message[:30]}...")
                            
                        elif chat_type == 'finetuning_rules':
                            FinetuningRuleQA.objects.create(
                                game_name=game_name,
                                question=message,
                                answer=response
                            )
                            logger.info(f"✅ 파인튜닝 QA 저장: {game_name} - {message[:30]}...")
                    except Exception as e:
                        logger.error(f"❌ QA 저장 실패: {str(e)}")
            else:
                response = "알 수 없는 채팅 타입입니다."
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"❌ 채팅 API 오류: {str(e)}")
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
            
            if not game_name:
                return JsonResponse({'error': '게임 이름이 필요합니다.'}, status=400)
            
            logger.info(f"📖 룰 요약 요청: {game_name} ({chat_type})")
            
            # 파인튜닝 타입 매핑
            api_chat_type = "finetuning" if chat_type == 'finetuning_rules' else "gpt"
            summary = rule_explanation_service.explain_game_rules(game_name, api_chat_type)
            
            return JsonResponse({
                'summary': summary,
                'game_name': game_name,
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
    """QR 코드 생성"""
    mobile_url = request.build_absolute_uri(reverse('chatbot:mobile_chat', args=[chat_type]))
    
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
