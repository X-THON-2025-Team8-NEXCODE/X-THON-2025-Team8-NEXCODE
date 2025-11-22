import os
import requests
from utils.db_utils import create_expenses_table, create_initial_table, insert_expenses_data, insert_initial_data, save_update_kakao_user, get_expenses
from utils.openai_utils import ask_ai, classify_category
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
import pymysql
import json
import sys
<<<<<<< Updated upstream
=======
from datetime import timedelta, datetime
>>>>>>> Stashed changes

if sys.stdout.encoding != 'utf-8':
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
if sys.stderr.encoding != 'utf-8':
	sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

def get_db_connection():
	try:
		conn = pymysql.connect(
			host="127.0.0.1",
			port=3306,
			user="nexcodecs",
			password="sprtmzhemWkd1234!!",
			db="xthon",
			charset="utf8mb4",
		)
		return conn
	except Exception as e:
		print(f"[ERROR] 데이터베이스 연결 오류: {e}")
		return None

client_id = "7cf0e1ebb6ff3e9c3cffcac43ae44e78"
client_secret = "4pGmDju9d4OKGXi2dXVs399ZDdIoU6mV"

domain = "https://x-thon.nexcode.kr:16010"
redirect_uri = domain + "/kakao/redirect"
kauth_host = "https://kauth.kakao.com"
kapi_host = "https://kapi.kakao.com"

@app.route('/debug', methods=['POST'])
def debug_post_request():

	headers = dict(request.headers)
	
	try:
		data = request.get_json()
		
		print(f"[DEBUG] Received POST Request (JSON):")
		print("--- Headers ---")
		print(json.dumps(headers, indent=2))
		print("--- Body (JSON) ---")
		print(json.dumps(data, indent=2, ensure_ascii=False))
		
		return jsonify({
			"status": "success",
			"message": "POST 요청 디버그 완료. 데이터가 서버 콘솔에 출력되었습니다.",
			"received_headers": headers,
			"received_body": data
		})

	except Exception as e:
		raw_data = request.data.decode('utf-8', errors='ignore')
		
		print(f"[DEBUG] Received POST Request (Non-JSON/Error):")
		print("--- Headers ---")
		print(json.dumps(headers, indent=2))
		print(f"--- Body (Raw Data) ---")
		print(raw_data)
		print(f"[ERROR] JSON Parsing Failed: {e}")
		
		return jsonify({
			"status": "fail",
			"cmd": 400,
			"message": "요청 본문이 JSON 형식이 아니거나 비어 있습니다.",
			"received_headers": headers,
			"received_raw_body": raw_data,
			"parsing_error": str(e)
		}), 400

@app.route("/kakao/authorize")
def authorize():
	scope_param = ""
	if request.args.get("scope"):
		scope_param = "&scope=" + request.args.get("scope")
	
	print(f"[Kakao] Redirecting to Kakao Login with client_id: {client_id}")
	
	# 파이썬 서버가 직접 리다이렉트 URL을 생성하여 브라우저를 카카오로 보냅니다.
	return redirect(
		"{0}/oauth/authorize?response_type=code&client_id={1}&redirect_uri={2}{3}".format(
			kauth_host, client_id, redirect_uri, scope_param
		)
	)

@app.route("/kakao/redirect")
def redirect_page():
    code = request.args.get("code")
    
    # 토큰 요청 데이터
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'client_secret': client_secret,
        'code': code
    }
    
    try:
        # A. 토큰 발급 요청
        resp = requests.post(kauth_host + "/oauth/token", data=data)
        
        if resp.status_code == 200:
            access_token = resp.json().get('access_token')
            session['access_token'] = access_token # 세션에 토큰 저장

            # B. [추가됨] 사용자 정보 요청 (v2/user/me)
            headers = {'Authorization': f'Bearer {access_token}'}
            user_resp = requests.get(kapi_host + "/v2/user/me", headers=headers)

            if user_resp.status_code == 200:
                user_info = user_resp.json()
                
                # 데이터 추출
                kakao_id = user_info.get('id')
                kakao_account = user_info.get('kakao_account', {})
                profile = kakao_account.get('profile', {})
                
                nickname = profile.get('nickname', 'Unknown')
                image = profile.get('profile_image_url', '')

                print(f"[Kakao] User Info: ID={kakao_id}, Nick={nickname}")

                # C. [추가됨] DB에 저장 또는 업데이트
                save_update_kakao_user(kakao_id, nickname, image)
                
                # D. [추가됨] 세션에 user_id 저장 (중요: 이후 사용자를 식별하기 위해)
                session['user_id'] = str(kakao_id)

                # E. 로그인 성공 시 메인 도메인으로 이동
                return redirect("https://x-thon.nexcode.kr")
            else:
                print(f"[Kakao] User Info Failed: {user_resp.text}")
                return redirect("https://naver.com")
        else:
            print(f"[Kakao] Token Failed: {resp.text}")
            return redirect("https://naver.com")
            
    except Exception as e:
        print(f"[Error] Login process error: {e}")
        return redirect("https://naver.com")
    
    
@app.route("/kakao/profile")
def profile():
	headers = {'Authorization': 'Bearer ' + session.get('access_token', '')}
	resp = requests.get(kapi_host + "/v2/user/me", headers=headers)
	return resp.text

@app.route("/kakao/logout")
def logout():
	headers = {'Authorization': 'Bearer ' + session.get('access_token', '')}
	resp = requests.post(kapi_host + "/v1/user/logout", headers=headers)
	session.pop('access_token', None)
	return resp.text

@app.route("/kakao/unlink")
def unlink():
	headers = {'Authorization': 'Bearer ' + session.get('access_token', '')}
	resp = requests.post(kapi_host + "/v1/user/unlink", headers=headers)
	session.pop('access_token', None)
	return resp.text


@app.route('/api/buy', methods=['POST'])
def buy():
	data = request.get_json()
 
	if not all(k in data for k in ["user_id", "merchant", "price", "hour", "created_at"]):
		return jsonify({"status": "fail", "message": "필수 데이터(user_id, merchant, price, hour, created_at)가 누락되었습니다."}), 400
    
	user_id = data.get("user_id")
	merchant = data.get("merchant")
	category = classify_category(merchant)
	price = data.get("price")
	hour = data.get("hour")
	sentiment = data.get("sentiment")
	regret_flag = data.get("regret_flag")
	created_at = data.get("created_at")
	
	print(category)
	
	try:
		create_expenses_table(user_id)
		insert_expenses_data(user_id, merchant, category, price, hour, sentiment, regret_flag, created_at)
		
		return jsonify({"status":"success","message":"구매 내역이 성공적으로 기록되었습니다."})
	except Exception as e:
		print(e)
		return jsonify({"status":"fail","message":f"구매 내역 기록 중 에러 발생: {str(e)}"})

@app.route('/api/expenses', methods=['POST'])
def expenses():
	data = request.get_json()
 
	if not all(k in data for k in ["user_id", "item_name", "price", "created_at"]):
		return jsonify({"status": "fail", "message": "필수 데이터(user_id, item_name, price, created_at)가 누락되었습니다."}), 400
	
	user_id = data.get("user_id")
	date = data.get("date")
	
	try:
		result = get_expenses(user_id, date)
		
		if result != None:
			jsonify({"status":"success","message":"해당 날짜의 지출 내역을 성공적으로 불러왔습니다.", "data": result})
		else:
			return jsonify({"status":"fail","message":"해당 날짜의 지출 내역이 없습니다."})
	except Exception as e:
		print(e)
		return jsonify({"status":"fail","message":f"초기 지출 내역 기록 중 에러 발생: {str(e)}"})

@app.route('/api/ai', methods=['POST'])
def ask():
    data = request.get_json()
    item = data.get("item")
    price = data.get("price")
    category = data.get("category")
    hour = data.get("hour")


    result = ask_ai(item, price, category, hour)
    
    if "error" in result:
        return jsonify({"status":"fail","message":f"에러 발생: {result['error']}"})
    else:
        return jsonify({"status":"success","ask":f"답변: {result['analysis']['message']}", "decision": f"판단: {result['decision']['verdict']} (위험도: {result['decision']['risk_score']})"})

<<<<<<< Updated upstream
=======
EXPENSES_INFO = {
    0: {"title": "메가커피", "amount": 3900, "category": "카페", "created_at": "2025-11-23 00:50:00"},
    1: {"title": "메가커피", "amount": 4500, "category": "카페", "created_at": "2025-11-23 00:50:00"},
    2: {"title": "넷플릭스", "amount": 13500, "category": "구독", "created_at": "2025-11-23 00:50:00"},
    3: {"title": "배달의 민족", "amount": 22000, "category": "배달", "created_at": "2025-11-23 00:50:00"},
    4: {"title": "배달의 민족", "amount": 12000, "category": "배달", "created_at": "2025-11-23 00:50:00"},
    5: {"title": "메가커피", "amount": 2800, "category": "카페", "created_at": "2025-11-23 00:50:00"},
    6: {"title": "넷플릭스", "amount": 9500, "category": "구독", "created_at": "2025-11-23 00:50:00"},
}

@app.route('/save_expenses', methods=['POST', 'OPTIONS'])
def save_expenses_api():
    try:
        data = request.json
        ids = data.get('ids', [])
        user_id = data.get('user_id')
        print(f"[1차 저장] 선택된 ID: {ids}")
        
        conn = pymysql.connect(
			host="127.0.0.1",
			port=3306,
			user="nexcodecs",
			password="sprtmzhemWkd1234!!",
			db="users",
			charset="utf8mb4",
		)
        cur_hour = datetime.now().hour
        saved_count = 0

        with conn.cursor() as cursor:
            for idx in ids:
                item = EXPENSES_INFO.get(int(idx))
                if item:
                    # 중복 확인 (이미 있으면 패스)
                    chk_sql = f"SELECT 1 FROM {user_id}_expenses WHERE merchant=%s AND price=%s AND created_at=%s"
                    cursor.execute(chk_sql, (item['title'], item['amount'], item['created_at']))
                    
                    if not cursor.fetchone():
                        # 없으면 기본값(sentiment=None, regret_flag=None)으로 저장
                        sql = f"""
                            INSERT INTO {user_id}_expenses (merchant, category, price, hour, created_at) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, (item['title'], item['category'], item['amount'], cur_hour, item['created_at']))
                        saved_count += 1
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "count": saved_count})
    except Exception as e:
        print(f"1차 저장 에러: {e}")
        return jsonify({"status": "error", "message": str(e)})


# =================================================================
# [2단계] 평가 결과 저장 (있으면 수정, 없으면 추가)
# =================================================================
@app.route('/save_evaluation', methods=['POST', 'OPTIONS'])
def save_evaluation_api():
    try:
        data = request.json
        results = data.get('results', []) # [{expenseIndex:0, decision:'satisfied'}, ...]
        user_id = data.get('user_id')
        print(f"[평가 저장] 결과: {results}")

        conn = pymysql.connect(
			host="127.0.0.1",
			port=3306,
			user="nexcodecs",
			password="sprtmzhemWkd1234!!",
			db="users",
			charset="utf8mb4",
		)
        cur_hour = datetime.now().hour

        with conn.cursor() as cursor:
            for res in results:
                idx = int(res['expenseIndex'])
                decision = res['decision']
                
                # 1. 평가 값을 DB 컬럼 형식으로 변환
                sentiment = None
                regret_flag = 0

                if decision == 'satisfied':
                    sentiment = '만족'
                    regret_flag = 0
                elif decision == 'regret':
                    sentiment = '후회'
                    regret_flag = 1
                elif decision == 'hold':
                    sentiment = '보류'
                    regret_flag = 0

                if idx in EXPENSES_INFO:
                    item = EXPENSES_INFO[idx]

                    # 2. [UPDATE 시도] : 이미 같은 내역이 있다면 sentiment랑 regret_flag만 수정
                    update_sql = f"""
                        UPDATE {user_id}_expenses
                        SET sentiment = %s, regret_flag = %s
                        WHERE merchant = %s AND price = %s AND created_at = %s
                    """
                    rows_affected = cursor.execute(update_sql, (
                        sentiment, 
                        regret_flag, 
                        item['title'], 
                        item['amount'], 
                        item['created_at']
                    ))

                    # 3. [INSERT 수행] : UPDATE된 줄이 없다면(데이터가 없다면) 새로 추가
                    if rows_affected == 0:
                        print(f"데이터 없음 -> 신규 추가: {item['title']}")
                        insert_sql = f"""
                            INSERT INTO {user_id}_expenses 
                            (merchant, category, price, hour, sentiment, regret_flag, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_sql, (
                            item['title'], 
                            item['category'], 
                            item['amount'], 
                            cur_hour, 
                            sentiment, 
                            regret_flag, 
                            item['created_at']
                        ))
                    else:
                        print(f"기존 데이터 업데이트: {item['title']}")

            conn.commit()
        conn.close()
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"평가 저장 실패: {e}")
        return jsonify({"status": "error", "message": str(e)})
>>>>>>> Stashed changes

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=16010, debug=False, ssl_context=('./cert_nexcode.kr/nexcode.kr.cer', './cert_nexcode.kr/nexcode.kr.key'))