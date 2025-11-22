from utils.openai_utils import ask_ai
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql

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
        print(f"데이터베이스 연결 오류: {e}")
        return None


@app.route('/', methods=['GET'])
def home():
    conn = get_db_connection()
    if conn:
        conn.close()
        db_status = "연결 성공"
    else:
        db_status = "연결 실패"

    return jsonify({
        "status": "success",
        "message": "Flask 서버가 정상적으로 실행 중입니다.",
        "db_connection_status": db_status
    })

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
    app.run(host="127.0.0.1", port=5000, debug=True)