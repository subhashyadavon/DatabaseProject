from flask import Flask, render_template, request, jsonify
from db_module import get_database

app = Flask(__name__)

# The factory handles selecting between SQLite, MSSQL, or Mock
db = get_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    search_type = data.get('type', 'title')
    
    if search_type == 'title':
        return jsonify(db.searchTitle(query))
    elif search_type == 'actor':
        return jsonify(db.actorMovies(query))
    elif search_type == 'director':
        return jsonify(db.directorMovies(query))
    elif search_type == 'language':
        return jsonify(db.languageTitle(query))
    return jsonify({"error": "Invalid search type"}), 400

@app.route('/api/stats/<stat_type>')
def get_stats(stat_type):
    stats_map = {
        'actors': db.topActors,
        'directors': db.topDirectors,
        'composers': db.topComposers,
        'writers': db.topWriters,
        'movies': db.topMovies,
        'genre': db.countGenre,
        'genre_decades': db.topGenreDecade,
        'runtime': db.topRuntime,
        'company': db.topCompany,
        'actor_director': db.topActorDirector,
        'cast_size': db.topCastSize
    }
    
    if stat_type in stats_map:
        return jsonify(stats_map[stat_type]())
    return jsonify({"error": "Invalid stat type"}), 400

@app.route('/api/admin/<action>', methods=['POST'])
def admin_action(action):
    if action == 'delete':
        return jsonify({"message": db.delete()})
    elif action == 'repopulate':
        return jsonify({"message": db.repopulate()})
    elif action == 'recreate':
        return jsonify({"message": db.recreate()})
    return jsonify({"error": "Invalid action"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
