from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BattedBallStat(db.Model):
    __tablename__ = 'batted_ball_stat'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    batter = db.Column(db.String(100))
    batter_id = db.Column(db.Integer)
    exit_direction = db.Column(db.Integer)
    exit_speed = db.Column(db.Float)
    game_date = db.Column(db.Date)
    hang_time = db.Column(db.Float)
    hit_distance = db.Column(db.Float)
    hit_spin_rate = db.Column(db.Float)
    launch_angle = db.Column(db.Float)
    pitcher = db.Column(db.String(100))
    pitcher_id = db.Column(db.Integer)
    play_outcome = db.Column(db.String(50))
    video_link = db.Column(db.String(255))
