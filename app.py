from flask import Flask, render_template, request
from config import Config
from models import db, BattedBallStat
import pandas as pd
import os
from sqlalchemy import text
import math

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///BBD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Global variable to cache the query result, allowing for quicker data retrieval
cached_stats = []

def load_data_from_excel(file_path):
    data = pd.read_excel(file_path)
    for index, row in data.iterrows():
        # Check if record already exists to prevent duplicates
        exists = BattedBallStat.query.filter_by(
            batter=row['BATTER'],
            game_date=row['GAME_DATE'],
            exit_speed=row['EXIT_SPEED'],
            launch_angle=row['LAUNCH_ANGLE']
        ).first()
        
        if not exists:
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

    sql = text(f"""
    SELECT batter, 
           COUNT(*) AS batted_ball_count,
           AVG(exit_speed) AS avg_exit_speed, 
           AVG(launch_angle) AS avg_launch_angle, 
           AVG(hit_distance) AS avg_hit_distance
    FROM batted_ball_stat
    GROUP BY batter
    HAVING COUNT(*) >= 10
    ORDER BY {order_by};
    """)
    
    result = db.session.execute(sql)
    cached_stats = [{'batter': row[0], 
                     'avg_exit_speed': row[2], 
                     'avg_launch_angle': row[3], 
                     'avg_hit_distance': row[4]} for row in result]

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
           exit_direction,
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
    player_stats = [{'exit_direction': row[1],
                     'exit_speed': row[2],
                     'launch_angle': row[3],
                     'hit_distance': row[4],
                     'game_date': row[5],
                     'play_outcome': row[6],
                     'video_link': row[7]} for row in result]

    # Calculate the percentage of hits in each exit direction quarter
    direction_counts = {
        '-45 to -22.5': 0,
        '-22.5 to 0': 0,
        '0 to 22.5': 0,
        '22.5 to 45': 0
    }
    total_hits = len(player_stats)
    
    for stat in player_stats:
        exit_direction = stat['exit_direction']
        if -45 <= exit_direction < -22.5:
            direction_counts['-45 to -22.5'] += 1
        elif -22.5 <= exit_direction < 0:
            direction_counts['-22.5 to 0'] += 1
        elif 0 <= exit_direction < 22.5:
            direction_counts['0 to 22.5'] += 1
        elif 22.5 <= exit_direction <= 45:
            direction_counts['22.5 to 45'] += 1
    
    direction_percentages = {key: (count / total_hits) * 100 for key, count in direction_counts.items()}

    # Calculate positions for plotting points on the diamond
    points = []
    for stat in player_stats:
        exit_direction = stat['exit_direction']
        hit_distance = stat['hit_distance']
        
        # Calculate the angle in radians
        angle_rad = math.radians(exit_direction)

        # Calculate x and y coordinates
        x = hit_distance * math.cos(angle_rad)
        y = -hit_distance * math.sin(angle_rad)  # Invert y-axis to match the diamond layout

        points.append((x, y))

    print(points)

    return render_template('player_stats.html', batter=batter, stats=player_stats, 
                           direction_percentages=direction_percentages, points=points)

if __name__ == "__main__":
    app.run(debug=True)
