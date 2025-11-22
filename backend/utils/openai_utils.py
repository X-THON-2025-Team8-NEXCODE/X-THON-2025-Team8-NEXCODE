import pymysql
import json
from openai import OpenAI

# ==========================================
# 1. 설정
# ==========================================
API_KEY = "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"
client = OpenAI(api_key=API_KEY)

# ==========================================
# 2. 시스템 프롬프트 (이모티콘 관련 지시 삭제)
# ==========================================
SYSTEM_PROMPT = """
# Role
당신은 사용자의 소비 패턴을 분석하여 구매 의사결정을 돕는 'AI 소비 코치'입니다.
상황에 따라 [과거 통계 데이터] 또는 [사용자 입력 기억]이 주어집니다.

# Decision Logic
### Scenario A: [과거 통계] 존재 (우선순위 1)
1. **Time Slot Check:** 현재 시간대가 포함된 구간의 데이터를 신뢰하세요.
2. **Risk Calculation:**
   - Regret Rate 70% 이상: [강력 비추천]
   - Regret Rate 30~70%: [신중 요망]
   - Regret Rate 30% 미만: [구매 추천]

### Scenario B: [과거 기억]만 존재 (우선순위 2)
1. **Similarity Check:** 현재 물건과 카테고리/시간대/가격이 유사한 기억을 찾으세요.
2. **Advice:** "과거에 OOO을 샀을 때도..."라며 구체적 사례를 들어 조언하세요.

# Output Format (JSON Only)
응답은 이모티콘 없이 텍스트로만 작성하세요.
{
  "decision": { "verdict": "강력 비추천 / 주의 / 추천", "risk_score": 0~100 },
  "analysis": { "message": "조언 내용 (이모티콘 제외)" }
}
"""

# ==========================================
# 3. DB 조회 로직 (원격 DB 연결)
# ==========================================
def get_context_from_db(category, hour, price):
    conn = pymysql.connect(
        host="secuho.life",
        port=53306,
        user="nexcodecs",
        password="sprtmzhemWkd1234!!",
        db="test_db",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            print(f"\n🔍 [DB 조회] 조건: 카테고리='{category}', 시간={hour}시")

            # [1단계] expenses 테이블 조회
            sql_stats = '''
                SELECT COUNT(*) as cnt, SUM(regret_flag) as regret_sum 
                FROM expenses 
                WHERE category = %s AND hour = %s
            '''
            cursor.execute(sql_stats, (category, hour))
            stat = cursor.fetchone()

            if stat and stat['cnt'] >= 3:
                total = stat['cnt']
                regret = float(stat['regret_sum']) if stat['regret_sum'] else 0
                regret_rate = int((regret / total) * 100)
                
                return {
                    "type": "STATS",
                    "data": {
                        "count": total, 
                        "regret_rate": regret_rate, 
                        "group": f"{category} {hour}시"
                    }
                }

            # [2단계] initial_memories 테이블 조회
            sql_memories = "SELECT * FROM initial_memories WHERE category = %s"
            cursor.execute(sql_memories, (category,))
            memories = cursor.fetchall()
            
            if memories:
                return {"type": "MEMORY", "data": memories}

            return {"type": "NONE", "data": None}
            
    finally:
        conn.close()

# ==========================================
# 4. AI 질문 로직
# ==========================================
def ask_ai_coach(item_name, price, category, current_hour):
    context = get_context_from_db(category, current_hour, price)
    
    user_msg = f"""
    [현재 질문]
    - 물건: {item_name}
    - 가격: {price}원
    - 카테고리: {category}
    - 현재 시간: {current_hour}시
    """
    
    if context["type"] == "STATS":
        stats = context["data"]
        user_msg += f"""
        \n[과거 통계 데이터 발견]
        - 그룹: {stats['group']}
        - 누적 데이터: {stats['count']}건
        - 후회율: {stats['regret_rate']}%
        """
        print(f"👉 통계 데이터 발견! 후회율 {stats['regret_rate']}%")

    elif context["type"] == "MEMORY":
        # 여기서 출력할 때도 이모티콘 없이 출력됨 (DB에 '후회'라고만 들어있으므로)
        mem_list = [
            f"- {m['item_name']} ({m['price']}원, {m['time_text']}) -> {m['sentiment']}" 
            for m in context['data']
        ]
        mem_str = "\n".join(mem_list)
        user_msg += f"""
        \n[과거 기억 데이터 발견]
        {mem_str}
        """
        print(f"👉 과거 기억 {len(context['data'])}건 발견.")
    
    else:
        user_msg += "\n[데이터 없음] 일반적인 조언 부탁해."
        print("👉 참고할 데이터 없음.")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 5. 실행 테스트
# ==========================================
def ask_ai(item, price, category, hour):
    print("\n🛒 [Pymysql 연동] AI 코치 시작 (이모티콘 제거 버전)")

    # 테스트 질문
    question_item = item
    question_price = price
    question_category = category
    question_hour = hour
    
    print(f"\nQ. {question_hour}시에 {question_category}({question_item}) 살까?")
    
    result = ask_ai_coach(question_item, question_price, question_category, question_hour)
    
    return result

def classify_category(text,):
    client = OpenAI(api_key=API_KEY)

    system_prompt = """
    #역할
    당신은 결제 내역을 분석하여 지정된 카테고리로 분류하는 정확한 AI입니다.
    입력된 텍스트를 분석하여 아래 5가지 카테고리 중 가장 적절한 하나를 선택하세요.

    #분류 기준 (Category List)
    식비: 식당, 카페, 술집, 배달앱, 편의점 음식 등
    교통: 택시, 버스, 지하철, 기차, 주유소, 킥보드 등
    여가: 영화, 넷플릭스, PC방, 노래방, 여행, 숙박, 공연 등
    패션: 의류, 신발, 가방, 액세서리, 미용실, 화장품 등
    기타: 위 4가지에 해당하지 않는 모든 내역 (송금, 의료, 교육, 전자제품 등)

    #출력 형식
    설명이나 부가적인 말 없이 오직 '카테고리명' 단어 하나만 출력하세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"