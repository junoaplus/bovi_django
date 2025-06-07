import httpx
import asyncio
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RunpodClient:
    """Runpod AI 백엔드와 통신하는 클라이언트"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'RUNPOD_API_URL', 'http://localhost:8000')
        self.timeout = getattr(settings, 'RUNPOD_TIMEOUT', 30.0)
        
        # HTTP 헤더 설정
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Django-BoardgameBot/1.0'
        }
        
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """HTTP 요청 공통 메서드"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == 'POST':
                    response = await client.post(url, json=data, headers=self.headers)
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"❌ Runpod API 타임아웃: {url}")
            raise Exception("AI 서버 응답 시간이 초과되었습니다.")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Runpod API HTTP 오류: {e.response.status_code} - {url}")
            raise Exception(f"AI 서버 오류가 발생했습니다: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"❌ Runpod API 연결 오류: {str(e)} - {url}")
            raise Exception("AI 서버에 연결할 수 없습니다.")
        except Exception as e:
            logger.error(f"❌ Runpod API 알 수 없는 오류: {str(e)} - {url}")
            raise Exception(f"AI 서버 통신 중 오류가 발생했습니다: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """AI 서버 상태 확인"""
        return await self._make_request('GET', '/health')
    
    async def recommend_games(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """게임 추천 요청"""
        data = {
            "query": query,
            "top_k": top_k
        }
        return await self._make_request('POST', '/recommend', data)
    
    async def explain_rules(self, game_name: str, question: str, chat_type: str = "gpt") -> Dict[str, Any]:
        """룰 설명 요청"""
        data = {
            "game_name": game_name,
            "question": question,
            "chat_type": chat_type
        }
        return await self._make_request('POST', '/explain-rules', data)
    
    async def get_rule_summary(self, game_name: str, chat_type: str = "gpt") -> Dict[str, Any]:
        """게임 룰 요약 요청"""
        data = {
            "game_name": game_name,
            "chat_type": chat_type
        }
        return await self._make_request('POST', '/rule-summary', data)
    
    async def get_available_games(self) -> Dict[str, Any]:
        """사용 가능한 게임 목록 요청"""
        return await self._make_request('GET', '/games')
    
    def sync_recommend_games(self, query: str, top_k: int = 3) -> str:
        """동기 버전 - 게임 추천"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.recommend_games(query, top_k))
            loop.close()
            
            if result.get('status') == 'success':
                return result.get('data', {}).get('recommendation', '추천을 가져올 수 없습니다.')
            else:
                return result.get('message', '추천 요청이 실패했습니다.')
                
        except Exception as e:
            logger.error(f"❌ 동기 게임 추천 실패: {str(e)}")
            return f"게임 추천 서비스에 연결할 수 없습니다: {str(e)}"
    
    def sync_explain_rules(self, game_name: str, question: str, chat_type: str = "gpt") -> str:
        """동기 버전 - 룰 설명"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.explain_rules(game_name, question, chat_type))
            loop.close()
            
            if result.get('status') == 'success':
                return result.get('data', {}).get('answer', '답변을 가져올 수 없습니다.')
            else:
                return result.get('message', '룰 설명 요청이 실패했습니다.')
                
        except Exception as e:
            logger.error(f"❌ 동기 룰 설명 실패: {str(e)}")
            return f"룰 설명 서비스에 연결할 수 없습니다: {str(e)}"
    
    def sync_get_rule_summary(self, game_name: str, chat_type: str = "gpt") -> str:
        """동기 버전 - 룰 요약"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_rule_summary(game_name, chat_type))
            loop.close()
            
            if result.get('status') == 'success':
                return result.get('data', {}).get('summary', '요약을 가져올 수 없습니다.')
            else:
                return result.get('message', '룰 요약 요청이 실패했습니다.')
                
        except Exception as e:
            logger.error(f"❌ 동기 룰 요약 실패: {str(e)}")
            return f"룰 요약 서비스에 연결할 수 없습니다: {str(e)}"
    
    def sync_get_available_games(self) -> list:
        """동기 버전 - 게임 목록"""
        try:
            logger.info(f"🎮 Runpod 게임 목록 요청: {self.base_url}/games")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_available_games())
            loop.close()
            
            if result.get('status') == 'success':
                games = result.get('data', {}).get('games', [])
                logger.info(f"✅ 게임 목록 수신: {len(games)}개")
                return games
            else:
                logger.warning(f"⚠️ Runpod 서버 응답 오류: {result.get('message', 'Unknown error')}")
                return self._get_fallback_games()
                
        except Exception as e:
            logger.error(f"❌ 동기 게임 목록 조회 실패: {str(e)}")
            return self._get_fallback_games()
    
    def _get_fallback_games(self) -> list:
        """폴백 게임 목록"""
        fallback_games = [
            "카탄", "스플렌더", "아줄", "윙스팬", "뱅", 
            "킹 오브 도쿄", "7 원더스", "도미니언", "스몰 월드", "티켓 투 라이드"
        ]
        logger.info(f"📋 폴백 게임 목록 사용: {len(fallback_games)}개")
        return fallback_games
    
    def sync_health_check(self) -> Dict[str, Any]:
        """동기 버전 - 헬스체크"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.health_check())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"❌ 헬스체크 실패: {str(e)}")
            return {"status": "error", "message": str(e)}
