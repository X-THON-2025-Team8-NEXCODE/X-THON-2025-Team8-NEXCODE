from utils.db_utils import create_expenses_table, create_initial_table, insert_expenses_data, insert_initial_data
from utils.openai_utils import ask_ai
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import json
import sys

if sys.stdout.encoding != 'utf-8':
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
if sys.stderr.encoding != 'utf-8':
	sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

app = Flask(__name__)
CORS(app)

def get_db_connection():
	try:
		conn = pymysql.connect(
			host="secuho.life",
			port=53306,
			user="nexcodecs",
			password="sprtmzhemWkd1234!!",
			db="xthon",
			charset="utf8mb4",
		)
		return conn
	except Exception as e:
		print(f"[ERROR] 데이터베이스 연결 오류: {e}")
		return None


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
  
@app.route('/api/buy', methods=['POST'])
def buy():
	data = request.get_json()
	user_id = data.get("user_id")
	merchant = data.get("merchant")
	category = data.get("category")
	price = data.get("price")
	hour = data.get("hour")
	sentiment = data.get("sentiment")
	regret_flag = data.get("regret_flag")
	created_at = data.get("created_at")
	
	try:
		create_expenses_table(user_id)
		insert_expenses_data(user_id, merchant, category, price, hour, sentiment, regret_flag, created_at)
		
		return jsonify({"status":"success","message":"구매 내역이 성공적으로 기록되었습니다."})
	except Exception as e:
		return jsonify({"status":"fail","message":f"구매 내역 기록 중 에러 발생: {str(e)}"})

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