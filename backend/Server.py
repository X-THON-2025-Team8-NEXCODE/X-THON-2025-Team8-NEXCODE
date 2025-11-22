import os
import requests
from utils.db_utils import create_expenses_table, create_initial_table, insert_expenses_data, insert_initial_data, save_update_kakao_user, get_expenses
from utils.openai_utils import ask_ai, classify_category
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
import pymysql
import json
import sys

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


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=16010, debug=False, ssl_context=('./cert_nexcode.kr/nexcode.kr.cer', './cert_nexcode.kr/nexcode.kr.key'))