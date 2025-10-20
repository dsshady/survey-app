from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__)

# 数据文件
DATA_FILE = "survey_results.json"

def init_data():
    """初始化数据结构"""
    if not os.path.exists(DATA_FILE):
        data = {
            "results": [],
            "distribution": {
                "excellent": 0,  # 90-98分人数
                "good_or_below": 0  # 30-89分人数
            },
            "settings": {
                "total_leaders": 6,
                "max_excellent": 2,
                "min_good_or_below": 4
            }
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    """加载数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """主页"""
    return send_from_directory('.', 'survey_final.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """静态文件服务"""
    return send_from_directory('.', filename)

@app.route('/api/submit', methods=['POST'])
def submit_scores():
    """提交评分"""
    try:
        # 获取请求数据
        data = request.get_json()
        responder_id = data.get('responder_id')
        scores = data.get('scores', [])
        
        # 验证输入
        if not responder_id:
            return jsonify({"success": False, "message": "请输入工号"}), 400
        
        if len(scores) != 6:
            return jsonify({"success": False, "message": "请为6位领导评分"}), 400
        
        # 检查分数范围
        for score in scores:
            if not (30 <= score <= 98):
                return jsonify({"success": False, "message": "分数必须在30-98之间"}), 400
        
        # 加载现有数据
        app_data = load_data()
        settings = app_data["settings"]
        
        # 计算本次提交的分布
        excellent_count = sum(1 for s in scores if 90 <= s <= 98)
        good_or_below_count = sum(1 for s in scores if 30 <= s <= 89)
        
        # 检查当前投票是否符合要求（2个优秀，4个良好及以下）
        if excellent_count > 2:
            return jsonify({"success": False, "message": "当前投票中优秀人数超过限制（最多2人）"}), 400
            
        if good_or_below_count < 4:
            return jsonify({"success": False, "message": "当前投票中良好及以下人数不足（至少4人）"}), 400
        
        # 保存结果
        app_data["results"].append({
            "responder_id": responder_id,
            "scores": scores,
            "timestamp": datetime.now().isoformat()
        })
        
        # 更新分布统计
        for score in scores:
            if 90 <= score <= 98:
                app_data["distribution"]["excellent"] += 1
            elif 30 <= score <= 89:
                app_data["distribution"]["good_or_below"] += 1
        
        save_data(app_data)
        
        return jsonify({"success": True, "message": "评议成功"})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/results')
def get_results():
    """获取结果（仅发起端）"""
    # 实际应用中需要身份验证
    # 这里简化处理，通过请求参数判断是否为发起端
    is_initiator = request.args.get('initiator') == 'true'
    
    if not is_initiator:
        return jsonify({"success": False, "message": "无权查看结果"}), 403
    
    try:
        data = load_data()
        return jsonify({
            "success": True,
            "distribution": data["distribution"],
            "results": data["results"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    init_data()
    app.run(debug=True, host='0.0.0.0', port=5000)