import sqlite3
from datetime import datetime


PATH_DATABASE = "db/montserrat4t.db"

def sql_init():
    conn = sqlite3.connect(PATH_DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id TEXT,
            post_id TEXT,
            post_date TEXT,
            reactions_count INTEGER,
            comments_count INTEGER
        )
    """
    )

    cursor.execute('''
          CREATE TABLE IF NOT EXISTS post_reactions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              post_profile TEXT,
              post_id TEXT,
              reaction_id INTEGER,
              profile_name TEXT,
              profile_url TEXT
          )
          ''')
    
    conn.close


def stats_(min_reactions):
    conn = sqlite3.connect(PATH_DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT profile_url, reaction_id, COUNT(*) AS count
        FROM post_reactions
        GROUP BY profile_url, reaction_id
        HAVING COUNT(*) >= ?
        ORDER BY count DESC
    ''', (int(min_reactions),))

    rows = cursor.fetchall()
    conn.close()

    return rows


def obtener_db_fbids():
    db_fbids = []

    conn = sqlite3.connect(PATH_DATABASE)
    cursor = conn.cursor()

    cursor.execute('SELECT profile_id, post_id FROM Posts')

    rows = cursor.fetchall()
    for row in rows:
        db_fbids.append((row[0], row[1]))

    conn.close()
    return db_fbids


def check_existing_post(post_id):
    conn = sqlite3.connect(PATH_DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Posts WHERE post_id=?", (post_id,))
    existing_post = cursor.fetchone()
    conn.close()
    return existing_post


def add_post_to_db(profile_id, post_id, post_date, count_reactions, count_comments):
    existing_post = check_existing_post(post_id)

    if existing_post:
        print(f"Duplicado {post_id}")
        return False

    fecha_datetime = datetime.strptime(post_date, '%Y-%m-%d %I:%M:%S %p %Z%z')
    fecha_formateada = fecha_datetime.strftime('%y-%m-%d %I:%M:%S %p')

    print(
        "Saving post details =>",
        profile_id,
        '\t',
        fecha_formateada,
        '\t',
        count_reactions,
        "\t\t",
        count_comments,
    )
    conn = sqlite3.connect(PATH_DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Posts (profile_id, post_id, post_date, reactions_count, comments_count) VALUES (?, ?, ?, ?, ?)",
        (profile_id, post_id, post_date, count_reactions, count_comments),
    )
    conn.commit()

    conn.close()

def add_reactions(post_profile,post_id, profiles):
    conn = sqlite3.connect(PATH_DATABASE)
    c = conn.cursor()

    for profile in profiles:
        c.execute(
            "INSERT INTO post_reactions (post_profile, post_id, reaction_id, profile_name, profile_url) VALUES (?, ?, ?, ?, ?)",
            (post_profile, post_id, profile["reaction_type"], profile["profile_name"], profile["profile_url"])
        )

    conn.commit()
    conn.close()