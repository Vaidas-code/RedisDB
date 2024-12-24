import re
import redis
from flask import Flask, request, jsonify

def user_key(user_id):
    return f"user#{user_id}"

def video_key(video_id):
    return f"video#{video_id}"

def create_app():
    app = Flask(__name__)
    redisClient = redis.Redis(host='redis', port=6379, decode_responses=True)

    #--------------------------------------------------------------------------------
    # USER PUT
    @app.route('/user', methods=['PUT'])
    def create_user():
        reqBody = request.json 
        user_id = reqBody.get("id")
        first_name = reqBody.get("firstName")
        last_name = reqBody.get("lastName")

        user_redis_key = user_key(user_id)

        if not user_id:
            return jsonify({"message": "Toks vartotojas jau egzistuoja arba nenurodytas vartotojo ID"}), 400
        if redisClient.exists(user_redis_key):
            return jsonify({"message": "Toks vartotojas jau egzistuoja arba nenurodytas vartotojo ID"}), 400

        user_data = {
            "firstName": first_name,
            "lastName": last_name
        }
        redisClient.hmset(user_redis_key, user_data)

        return jsonify({
            "message": "Vartotojo registracija sekminga"
        }), 200


    #----------------------------------------------------------------------------------
    # USER/USERID DELETE
    @app.route('/user/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        user_redis_key = user_key(user_id)

        user_exists = redisClient.exists(user_redis_key)
    
        if user_exists:
            redisClient.delete(user_redis_key)  
            return jsonify({"message": "Paskyra panaikinta sėkmingai"}), 200
        else:
            return jsonify({"message": "Paskyra nerasta"}), 404 
        
    #----------------------------------------------------------------------------------------------------
    # USER/USERID/VIEWS GET
    @app.route('/user/<user_id>/views', methods=['GET'])
    def get_user_views(user_id):
        user_redis_key = user_key(user_id)

        if not redisClient.exists(user_redis_key):
            return jsonify({"message": "Toks vartotojas neegzistuoja sistemoje"}), 404 

        views_key = f"{user_redis_key}:views"

        if not redisClient.exists(views_key):
            return jsonify({
                "viewedVideos": []
            }), 200
        
        viewed_videos = redisClient.lrange(views_key, 0, -1)

        return jsonify({
            "viewedVideos": viewed_videos
        }), 200


    #------------------------------------------------------------------------------------------
    # VIDEO PUT
    @app.route('/video', methods=['PUT'])
    def create_video():
        reqBody = request.json
        video_id = reqBody.get("id")
        description = reqBody.get("description")
        length_in_s = reqBody.get("lengthInS")

        video_redis_key = video_key(video_id)

        if redisClient.exists(video_redis_key):
            return jsonify({"message": "Toks video jau egzistuoja"}), 400

        video_data = {
            "description": description,
            "lengthInS": length_in_s
        }
        redisClient.hmset(video_redis_key, video_data)

        return jsonify({
            "message": "Video įregistruotas sekmingai"
        }), 200 


    #---------------------------------------------------------------------------------------------------------
    # GET VIDEO/ID
    @app.route('/video/<video_id>', methods=['GET'])
    def get_video(video_id):
        video_redis_key = video_key(video_id)

        if not redisClient.exists(video_redis_key):
            return jsonify({"message": "Video nerastas"}), 404

        video_data = redisClient.hgetall(video_redis_key) 

        return jsonify({
            "id": video_id,
            "description": video_data.get("description"),
            "lengthInS": video_data.get("lengthInS")
        }), 200 


    #-------------------------------------------------------------------------------------------
    # GET VIDEO/ID/VIEWS
    @app.route('/video/<video_id>/views', methods=['GET'])
    def get_video_views(video_id):
        video_redis_key = video_key(video_id)
        if not redisClient.exists(video_redis_key):
            return jsonify({"message": "Toks video neegzistuoja sistemoje"}), 404

        views_key = f"{video_redis_key}:views"

        if not redisClient.exists(views_key):
            return jsonify({
                "views": 0  
            }), 200
        
        views_count = redisClient.llen(views_key)

        return jsonify({
            "views": views_count  
        }), 200 
    


    #---------------------------------------------------------------------------------------------------
    # POST VIDEO/ID/VIEWS
    @app.route('/video/<video_id>/views', methods=['POST'])
    def add_video_view(video_id):
        reqBody = request.json
        user_id = reqBody.get("userId")

        video_redis_key = video_key(video_id)
        user_redis_key = user_key(user_id)

        if not redisClient.exists(video_redis_key):
            return jsonify({"message": "Tokio video nera"}), 404

        if not redisClient.exists(user_redis_key):
            return jsonify({"message": "Toks vartotojas neegzistuoja"}), 404

        views_key = f"{video_redis_key}:views"
        redisClient.rpush(views_key, user_id)

        video_data = redisClient.hgetall(video_redis_key)
        video_description = video_data.get("description", f"video_{video_id}") 

        user_views_key = f"{user_redis_key}:views"
        redisClient.rpush(user_views_key, video_description)

        return jsonify({
            "message": "Peržiūra įregistruota",
        }), 200



    #--------------------------------------------------------------------------------------------------------
    # FLUSH
    @app.route('/flushall', methods=['POST'])
    def flush_database():
        redisClient.flushall()
        return jsonify({"message": "Duomenų bazė išvalyta sėkmingai"}), 200

    return app 

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
