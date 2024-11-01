from flask import Flask, render_template, request
from config import Config
from models import db, BattedBallStat
import pandas as pd
import os
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BBD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Global variable to cache the query result, allowing for quicker data retrival
cached_stats = []

def load_data_from_excel(file_path):
    data = pd.read_excel(file_path)
    for index, row in data.iterrows():
        stat = BattedBallStat(
            batter=row['BATTER'],
            batter_id=row['BATTER_ID'],
            exit_direction=row['EXIT_DIRECTION'],
            exit_speed=row['EXIT_SPEED'],
            game_date=row['GAME_DATE'],
            hang_time=row['HANG_TIME'],
            hit_distance=row['HIT_DISTANCE'],
            hit_spin_rate=row['HIT_SPIN_RATE'],
            launch_angle=row['LAUNCH_ANGLE'],
            pitcher=row['PITCHER'],
            pitcher_id=row['PITCHER_ID'],
            play_outcome=row['PLAY_OUTCOME'],
            video_link=row['VIDEO_LINK']
        )
        db.session.add(stat)
    db.session.commit()

def init_db():
    if not os.path.exists('BBD.db'):
        with app.app_context():
            db.create_all()
            load_data_from_excel('data/BattedBallData.xlsx')
            print("Database initialized")

def load_cached_stats(sort_column='avg_exit_speed', sort_order='desc'):
    global cached_stats
    order_by = f"{sort_column} {'ASC' if sort_order == 'asc' else 'DESC'}"
    
    """for unknown reasons, the count that a batter appears is multiplied by 48. 
    so for qualified hitters, multiply 10*48=480 to get hitters with 10+ batted balls."""

    sql = text(f"""
    SELECT batter, 
           COUNT(*) AS batted_ball_count,
           AVG(exit_speed) AS avg_exit_speed, 
           AVG(launch_angle) AS avg_launch_angle, 
           AVG(hit_distance) AS avg_hit_distance
    FROM batted_ball_stat
    GROUP BY batter
    HAVING COUNT(*) >= 480
    ORDER BY {order_by};
    """)
    
    result = db.session.execute(sql)
    cached_stats = [{'batter': row[0], 
                     'avg_exit_speed': row[2], 
                     'avg_launch_angle': row[3], 
                     'avg_hit_distance': row[4]} for row in result]
    #print(cached_stats)

# Initialize the database and load cached data when the app starts
with app.app_context():
    init_db()

@app.route('/')
def index():
    sort_column = request.args.get('sort', 'avg_exit_speed')
    sort_order = request.args.get('order', 'desc')

    load_cached_stats(sort_column, sort_order)
    return render_template('index.html', stats=cached_stats)

@app.route('/player/<batter>')
def player_stats(batter):
    # Fetch individual stats for the selected player
    sql = text("""
    SELECT batter, 
           exit_speed,
           launch_angle,
           hit_distance,
           game_date,
           play_outcome,
           video_link
    FROM batted_ball_stat
    WHERE batter = :batter
    """)
    result = db.session.execute(sql, {'batter': batter})
    player_stats = [{'exit_speed': row[1],
                     'launch_angle': row[2],
                     'hit_distance': row[3],
                     'game_date': row[4],
                     'play_outcome': row[5],
                     'video_link': row[6]} for row in result]
    print(len(player_stats))
    return render_template('player_stats.html', batter=batter, stats=player_stats)

if __name__ == "__main__":
    app.run(debug=True)
