import google.generativeai as genai
import base64
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()


class OCRService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-flash-latest")
        else:
            self.model = None

    async def process_image(self, base64_image: str) -> dict:
        """Base64 이미지를 분석하여 영수증 정보를 추출합니다."""

        if not self.model:
            return {
                "success": False,
                "storeName": None,
                "cardName": None,
                "items": [],
                "rawText": "",
                "purchaseDateTime": None,
                "error": "GEMINI_API_KEY가 설정되지 않았습니다."
            }

        try:
            # base64 헤더 제거
            if "," in base64_image:
                base64_image = base64_image.split(",")[1]

            # 이미지 데이터 준비
            image_data = base64.b64decode(base64_image)

            prompt = """이 영수증 이미지를 분석해서 상품 정보를 추출해주세요.

영수증 형식:
- 각 상품은 2줄로 구성됩니다
- 1줄: 번호(NO)와 상품명
- 2줄: 바코드, 단가, 수량, 금액

다음 JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{
  "storeName": "상호명",
  "cardName": "카드명",
  "items": [
    {
      "no": "001",
      "name": "상품명",
      "barcode": "1234567890123",
      "unitPrice": 1000,
      "quantity": 1,
      "amount": 1000
    }
  ],
  "purchaseDateTime": "YY-MM-DD HH:MM",
  "rawText": "영수증 전체 텍스트"
}

주의사항:
- 숫자에서 콤마(,)는 제거하고 정수로 변환
- 바코드가 없으면 null
- 상품 정보가 없으면 빈 배열 []
- rawText에는 인식된 전체 텍스트 포함
- storeName: 영수증 상단의 상호명/매장명 (예: "케이할인마트", "이마트" 등)
- cardName: 결제에 사용된 카드명 또는 카드사 (예: "신한카드", "롯데카드", "하나카드" 등). 현금 결제면 "현금"
- purchaseDateTime: 영수증의 구매 날짜와 시간을 "YY-MM-DD HH:MM" 형식으로 변환 (예: "25-02-02 14:30")
- 찾을 수 없는 정보는 null
"""

            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ])

            # 응답 파싱
            response_text = response.text.strip()

            # JSON 블록 추출 (```json ... ``` 형식 처리)
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            if json_match:
                response_text = json_match.group(1)

            # JSON 파싱
            result = json.loads(response_text)

            return {
                "success": True,
                "storeName": result.get("storeName", None),
                "cardName": result.get("cardName", None),
                "items": result.get("items", []),
                "rawText": result.get("rawText", ""),
                "purchaseDateTime": result.get("purchaseDateTime", None),
                "error": None
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "storeName": None,
                "cardName": None,
                "items": [],
                "rawText": response_text if 'response_text' in locals() else "",
                "purchaseDateTime": None,
                "error": f"JSON 파싱 오류: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "storeName": None,
                "cardName": None,
                "items": [],
                "rawText": "",
                "purchaseDateTime": None,
                "error": f"OCR 처리 오류: {str(e)}"
            }
