CREATE DATABASE IF NOT EXISTS video_survey;
USE video_survey;

CREATE TABLE IF NOT EXISTS surveys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS survey_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    question_text TEXT,
    question_order INT,
    FOREIGN KEY (survey_id) REFERENCES surveys(id)
);

CREATE TABLE IF NOT EXISTS survey_submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    ip_address VARCHAR(50),
    device VARCHAR(100),
    browser VARCHAR(100),
    os VARCHAR(100),
    location VARCHAR(100),
    started_at DATETIME,
    completed_at DATETIME,
    overall_score INT,
    FOREIGN KEY (survey_id) REFERENCES surveys(id)
);

CREATE TABLE IF NOT EXISTS survey_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT,
    question_id INT,
    answer ENUM('Yes','No'),
    face_detected BOOLEAN,
    face_score INT,
    face_image_path TEXT,
    FOREIGN KEY (submission_id) REFERENCES survey_submissions(id),
    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
);

CREATE TABLE IF NOT EXISTS media_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT,
    type ENUM('video','image'),
    path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES survey_submissions(id)
);
