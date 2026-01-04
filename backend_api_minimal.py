"""
最小化后端 API - 用于测试 Render 部署
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Render 环境变量
API_PORT = int(os.getenv('PORT', '10000'))
API_HOST = os.getenv('HOST', '0.0.0.0')

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': '职场情绪充电站 API 服务（最小化版本）',
        'service': 'Agent API'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'API 服务正常运行',
        'timestamp': str(os.environ.get('START_TIME', 'unknown'))
    })

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': '测试成功！部署正常！'
    })

if __name__ == '__main__':
    app.config['START_TIME'] = str(os.environ.get('START_TIME', 'now'))
    app.run(host=API_HOST, port=API_PORT, debug=False)
