try:
        user_data = get_user_data(email)
        last_mouth_direction = user_data["last_mouth_direction"]
        mouth_start_time = float(user_data["gaze_start_time"])
    except Exception as e:
        print(f"Error :{e}")