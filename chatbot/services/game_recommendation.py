import logging
from django.conf import settings
from .runpod_client import RunpodClient

logger = logging.getLogger(__name__)

class GameRecommendationService:
    """게임 추천 서비스 - Runpod 백엔드 연동"""
    
    def __init__(self):
        # Runpod 클라이언트 초기화
        self.runpod_client = RunpodClient()
        
        # 폴백 옵션 설정
        self.use_fallback = getattr(settings, 'RUNPOD_USE_FALLBACK', True)
        
        logger.info("✅ 게임 추천 서비스가 초기화되었습니다.")
        
    def recommend_games(self, query):
        """게임 추천 메인 함수"""
        try:
            # Runpod 백엔드로 요청
            logger.info(f"🎮 게임 추천 요청: {query}")
            result = self.runpod_client.sync_recommend_games(query)
            logger.info("✅ 게임 추천 완료")
            return result
            
        except Exception as e:
            logger.error(f"❌ 게임 추천 실패: {str(e)}")
            
            # 폴백 옵션이 활성화된 경우 기본 응답 제공
            if self.use_fallback:
                return self._get_fallback_recommendation(query)
            else:
                return f"게임 추천 서비스에 일시적인 문제가 발생했습니다: {str(e)}"
    
    def _get_fallback_recommendation(self, query):
        """폴백 게임 추천 (Runpod 서버 다운 시)"""
        fallback_games = {
            "2명": ["패치워크", "7 원더스 듀얼", "쟤이푸르"],
            "전략": ["카탄", "윙스팬", "스플렌더"],
            "파티": ["코드네임", "텔레스트레이션", "딕싯"],
            "협력": ["팬데믹", "금지된 섬", "스피릿 아일랜드"],
            "빠른": ["스플렌더", "아줄", "킹 오브 도쿄"]
        }
        
        # 키워드 매칭으로 기본 추천
        for keyword, games in fallback_games.items():
            if keyword in query:
                recommendations = "\n".join([f"{game}: {keyword} 게임으로 추천합니다." for game in games])
                return f"🎮 기본 추천 (AI 서버 연결 불가):\n\n{recommendations}"
        
        # 기본 추천
        return "🎮 기본 추천 (AI 서버 연결 불가):\n\n카탄: 전략적이고 재미있는 게임\n스플렌더: 간단하면서도 깊이 있는 게임\n아줄: 아름다운 타일 놓기 게임"
    
    def get_service_status(self):
        """서비스 상태 확인"""
        try:
            health = self.runpod_client.sync_health_check()
            return {
                "status": "healthy" if health.get("status") == "healthy" else "degraded",
                "backend": "runpod",
                "details": health
            }
        except Exception as e:
            return {
                "status": "error",
                "backend": "runpod",
                "error": str(e)
            }
