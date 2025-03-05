from flask import Flask,request,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
# import MySQLdb

app=Flask(__name__)

# MySQL 所在的主机
HOSTNAME = "127.0.0.1"
# MySQL 的端口，默认是 3306
PORT = 3306
# 连接 MySQL 的用户名
USERNAME = "root"
# 连接 MySQL 的密码
PASSWORD = "123456"
# 数据库名称
DATABASE = "database_learn"

# 拼接成 SQLAlchemy 所需的连接 URI
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
)
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
# )
  
# 是否追踪对象的修改，通常设置为 False 以节省资源
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)

# with app.app_context():
#     with db.engine.connect() as connection:
#         r = connection.execute(text("SELECT 1"))
#         print(r.fetchall())
class User(db.Model):
	__tablename__="user"
	id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	username=db.Column(db.String(100),nullable=False)
	age=db.Column(db.Integer,nullable=False)
	
class Article(db.Model):
	__tablename__="article"
	id=db.Column(db.Integer,primary_key=True,autoincrement=True)
	title=db.Column(db.String(100),nullable=False)
	content=db.Column(db.Text,nullable=False)
	#添加作者外键
	author_id=db.Column(db.Integer,db.ForeignKey("user.id"))
	author=db.relationship("User",backref=db.backref("articles"))
with app.app_context():
	db.create_all()

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/user/add')
def add_user():
	user=User(username="zhangsan",age=18)
	db.session.add(user)
	db.session.commit()
	return "用户添加成功!"

@app.route('/user/query')
def query_usesr():
	##1.get查找,根据主键查找,查一条
	user=User.query.get(1)
	print(f"ID:{user.id},姓名:{user.username},年龄:{user.age}")
	##2.filter_by查找
	users=User.query.filter_by(username="zhangsan") #user类似于数组
	##3.all()查找
	users=User.query.all()   
	for user in users:
		print(f"ID:{user.id},姓名:{user.username},年龄:{user.age}")
	return "查询成功!"

@app.route('/user/update')
def update_user():
	# user=User.query.get(1)
	user=User.query.filter_by(username="zhangsan").first()
	user.age=20
	db.session.commit()
	return "修改成功!"

@app.route('/user/delete')
def delete_user():
	user=User.query.get(1)
	db.session.delete(user)
	db.session.commit()
	return "删除成功!"

if __name__ == '__main__':
	app.run(debug=True)

# @app.route('/about/<id>')
# def about(id):
# 	return f"About {id}"

# @app.route('/book/list')
# def book_list():
# 	page=request.args.get("page",default=1,type=int)
# 	return f"您获取第{page}页的图书列表!"
# ##1.debug
# ##2.修改host,端口号 

#################################
# import base64
# import uuid
# from flask import Flask, request, jsonify

# app = Flask(__name__)
# app.config["SECRET_KEY"] = "yoursecret"  # 若需会话/加密可用

# # ==========
# # 1. 用于演示的“会话存储”，把拍摄建议等信息暂存在内存
# #    真实项目中可用数据库或缓存替代
# #    session_data[session_id] = {
# #       "original_score": float,
# #       "advice": str,
# #       "movement_checked": bool,   # 用户是否已按建议移动
# #       "new_score": float         # 第二次评分
# #    }
# # ==========
# session_data = {}

# # ==========
# # 2. 这里用一个"假"的大模型调用函数做示例
# #    你要把它替换成真是的AI服务，例如OpenAI、Baidu、阿里等
# # ==========
# def call_large_model_for_image_score(image_bytes):
#     """
#     传入图像数据, 返回(美学评分, 移动建议)。
#     实际中你可能会:
#       - 调用图像质量评估模型(打分)
#       - 调用自然语言模型(给移动建议)
#     这里只是返回示例数据.
#     """
#     # 假设我们给它一个随机分数, 并给出一个随意的建议:
#     fake_score = 60.0  # 这里写死60分做示例
#     fake_advice = "请向左微倾手机，并稍微抬高一点拍摄角度。"
#     return fake_score, fake_advice

# def call_large_model_for_new_score(image_bytes, old_score):
#     """
#     第二次评分(用户已移动后再次拍照)，可对比旧分数或重新评估
#     """
#     # 这里写死做示例:
#     improved_score = old_score + 10  # 假设提高10分
#     return improved_score

# def call_large_model_check_movement(sensor_data, advice):
#     """
#     判断用户的传感器数据(sensor_data)是否满足'advice'中的移动建议
#     实际可用算法/AI/NLP 等解析用户的移动情况
#     这里我们简单示例: 如果 sensor_data 里包含 "left" 就算成功
#     """
#     if "left" in sensor_data.lower():
#         return True
#     return False

# # ==========
# # 3. 接口一：上传照片，得到第1次评分和移动建议
# #    - 路径: POST /api/upload_photo
# #    - 请求体: JSON, 包含base64图片数据, 例如:
# #        {
# #          "image_base64": "xxxxxx..."
# #        }
# #    - 响应: JSON
# #        {
# #          "session_id": <str>,
# #          "score": <float>,
# #          "advice": <str>
# #        }
# # ==========
# @app.route("/api/upload_photo", methods=["POST"])
# def upload_photo():
#     data = request.get_json()
#     if not data or "image_base64" not in data:
#         return jsonify({"error": "missing 'image_base64' field"}), 400

#     image_b64 = data["image_base64"]
#     try:
#         # 解码base64为二进制图像
#         image_bytes = base64.b64decode(image_b64)
#     except Exception as e:
#         return jsonify({"error": f"Invalid base64 data: {str(e)}"}), 400

#     # 调用大模型/算法做图像评分 & 提建议
#     score, advice = call_large_model_for_image_score(image_bytes)

#     # 生成一个会话ID, 用于后续检测动作 & 2次评分
#     session_id = str(uuid.uuid4())

#     # 存储到内存(示例)
#     session_data[session_id] = {
#         "original_score": score,
#         "advice": advice,
#         "movement_checked": False,
#         "new_score": None
#     }

#     return jsonify({
#         "session_id": session_id,
#         "score": score,
#         "advice": advice
#     })

# # ==========
# # 4. 接口二：用户上传传感器数据(如陀螺仪), 后端判断是否按建议移动
# #    - 路径: POST /api/check_movement
# #    - 请求体: JSON:
# #        {
# #          "session_id": "xxx-xxxx-xxx",
# #          "sensor_data": "some sensor info"
# #        }
# #    - 响应:
# #        {
# #          "success": bool,
# #          "message": str
# #        }
# # ==========
# @app.route("/api/check_movement", methods=["POST"])
# def check_movement():
#     data = request.get_json()
#     if not data or "session_id" not in data or "sensor_data" not in data:
#         return jsonify({"error": "Need 'session_id' and 'sensor_data'"}), 400

#     sid = data["session_id"]
#     sensor_data = data["sensor_data"]

#     if sid not in session_data:
#         return jsonify({"error": "Invalid session_id"}), 400

#     record = session_data[sid]
#     # 判断用户是否已经通过动作校验(避免重复检查)
#     if record["movement_checked"]:
#         return jsonify({"success": True, "message": "Movement already confirmed."})

#     # 利用大模型/算法判断传感器数据是否符合advice
#     # (这里简单用字符串匹配做示例)
#     advice = record["advice"]
#     moved_correctly = call_large_model_check_movement(sensor_data, advice)

#     if moved_correctly:
#         record["movement_checked"] = True
#         return jsonify({
#             "success": True,
#             "message": "Movement matched the advice! Now you can upload a new photo."
#         })
#     else:
#         return jsonify({
#             "success": False,
#             "message": "Your movement did not match the advice."
#         })

# # ==========
# # 5. 接口三：用户再上传“移动后”的照片，得到新的评分
# #    - 路径: POST /api/upload_new_photo
# #    - 请求体: JSON:
# #        {
# #          "session_id": "xxx-xxxx-xxx",
# #          "image_base64": "xxxx..."
# #        }
# #    - 响应:
# #        {
# #          "new_score": <float>,
# #          "old_score": <float>
# #        }
# #    - 前提: 要先经过check_movement成功
# # ==========
# @app.route("/api/upload_new_photo", methods=["POST"])
# def upload_new_photo():
#     data = request.get_json()
#     if not data or "session_id" not in data or "image_base64" not in data:
#         return jsonify({"error": "Need 'session_id' and 'image_base64'"}), 400

#     sid = data["session_id"]
#     if sid not in session_data:
#         return jsonify({"error": "Invalid session_id"}), 400

#     record = session_data[sid]
#     if not record["movement_checked"]:
#         return jsonify({"error": "You have not completed movement check or failed it."}), 400

#     image_b64 = data["image_base64"]
#     try:
#         image_bytes = base64.b64decode(image_b64)
#     except Exception as e:
#         return jsonify({"error": f"Invalid base64 data: {str(e)}"}), 400

#     old_score = record["original_score"]

#     # 调用大模型计算新的评分
#     new_score = call_large_model_for_new_score(image_bytes, old_score)
#     record["new_score"] = new_score

#     return jsonify({
#         "old_score": old_score,
#         "new_score": new_score
#     })


# # ==========
# # 6. 运行
# # ==========
# if __name__ == "__main__":
#     # Debug模式仅供开发调试, 生产环境请用更安全的方式部署
#     app.run(host="0.0.0.0", port=5000, debug=True)



########################################
# import os
# import openai
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# # 方式1: 从环境变量读取 OPENAI_API_KEY
# #   os.environ["OPENAI_API_KEY"] = "sk-xxxx"
# #   openai.api_key = os.getenv("OPENAI_API_KEY")

# # 方式2: 直接硬编码(不推荐在生产环境中这么做)
# openai.api_key = "sk-xxxx"

# @app.route("/")
# def index():
#     return "Hello! This is a ChatGPT API example."

# @app.route("/chat", methods=["POST"])
# def chat():
#     """
#     从请求体中获取 prompt，调用ChatGPT接口，返回回答。
    
#     JSON示例：
#     {
#       "prompt": "请介绍一下Python"
#     }
#     """
#     data = request.get_json()
#     if not data or "prompt" not in data:
#         return jsonify({"error": "Missing 'prompt' field in JSON"}), 400

#     prompt = data["prompt"]

#     try:
#         # 调用OpenAI的文本接口 (示例：text-davinci-003)
#         # 如果想使用gpt-3.5-turbo, 需用 ChatCompletion API, 见后文示例。
#         response = openai.Completion.create(
#             model="text-davinci-003",     # 或者 "gpt-3.5-turbo", "gpt-4"（需权限）
#             prompt=prompt,
#             max_tokens=1000,
#             temperature=0.7
#         )

#         # 从response中提取模型生成的文本
#         generated_text = response["choices"][0]["text"].strip()

#         return jsonify({"prompt": prompt, "answer": generated_text})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# # 如果要用 gpt-3.5-turbo (ChatCompletion) 而不是 text-davinci-003：
# # @app.route("/chat2", methods=["POST"])
# # def chat2():
# #     data = request.get_json()
# #     prompt = data.get("prompt", "")
# #     try:
# #         response = openai.ChatCompletion.create(
# #             model="gpt-3.5-turbo",
# #             messages=[
# #                 {"role": "user", "content": prompt}
# #             ],
# #             max_tokens=1000,
# #             temperature=0.7
# #         )
# #         generated_text = response["choices"][0]["message"]["content"].strip()
# #         return jsonify({"prompt": prompt, "answer": generated_text})
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
