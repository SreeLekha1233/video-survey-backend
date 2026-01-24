import os
import mysql.connector


# def get_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="sreeroot@123",
#         database="video_survey"
#     )


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "video_survey"),
        port=3306
    )