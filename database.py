import sqlite3
import random
from typing import Literal, Callable
from functools import wraps


# def with_db_connection(func: Callable) -> Callable:
#     @wraps(func)
#     def wrapper(*args, ** kwargs):
#         con = sqlite3.connect('db.db')
#         cur = con.cursor()
#         try:
#             result = func(cur, *args, **kwargs)
#             con.commit()
#         except Exception as e:
#             con.rollback()
#             print(f'ОШИБКА: {e}')
#         finally:
#             con.close()
#         return result
#     return wrapper


def with_db_connection(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        con = sqlite3.connect("db.db")
        cur = con.cursor()
        result = None
        try:
            result = func(cur, *args, **kwargs)
            con.commit()
        except Exception as e:
            con.rollback()
            print(f"ОШИБКА: {e}")
        finally:
            con.close()
        return result
    return wrapper 

@with_db_connection
def create_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS players(
        player_id INTEGER,
        username TEXT,
        role TEXT,
        mafia_vote INTEGER,
        citizen_vote INTEGER,
        voted INTEGER,
        dead INTEGER
    )""")

@with_db_connection
def insert_player(cur, player_id: int, username: str) -> None:
    sql = "INSERT INTO players (player_id, username, mafia_vote, citizen_vote, voted, dead) VALUES (?, ?, ?, ?, ?, ?)"
    cur.execute(sql, (player_id, username, 0, 0, 0, 0))

@with_db_connection
def players_amount(cur) -> str:
    sql = 'SELECT * FROM players'
    cur.execute(sql)
    res = cur.fetchall()
    return len(res)

@with_db_connection
def get_mafia_usernames(cur) -> str:
    sql = "SELECT username FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    data = cur.fetchall()
    names = ""
    for row in data:  #[(asdasasdas),]
        name = row[0]
        names += name + '\n'
    return names

@with_db_connection
def get_players_roles(cur) -> list:
    sql = 'SELECT player_id, role FROM players'
    cur.execute(sql)
    data = cur.fetchall()
    return data

@with_db_connection
def get_all_alive(cur) -> list:
    sql = 'SELECT username FROM players WHERE dead=0'
    cur.execute(sql)
    data = cur.fetchall() #[(Никита,), (Артем,),....]
    data = [row[0] for row in data]
    return data

@with_db_connection
def set_roles(cur, players: int) -> None:
    game_roles = ['citizen'] * players
    mafias = int(players * 0.3)
    for i in range(mafias):
        game_roles[i] = 'mafia'
    random.shuffle(game_roles)
    cur.execute('SELECT player_id FROM players')
    players_id = cur.fetchall()
    for role, player_id in zip(game_roles, players_id):
        sql = 'UPDATE  players SET role=? WHERE player_id=?'
        cur.execute(sql, (role, player_id[0]))

# @with_db_connection
# def vote(cur, type: Literal['mafia_vote', 'citizen_vote'], username: str, player_id: int) -> bool:
#     cur.execute('SELECT username FROM players WHERE player_id=? AND dead=0 AND voted=0', (player_id,))
#     can_vote = cur.fetchall()
#     if can_vote:
#         cur.execute(f'UPDATE players SET {type} = {type} + 1 WHERE username=?', (username,))
#         cur.execute('UPDATE players SET voted=1 WHERE player_id=?', (player_id,))
#         return True
#     return False

# @with_db_connection
# def mafia_kill(cur) -> str:
#     cur.execute('SELECT MAX(mafia_vote) FROM players')
#     max_votes = cur.fetchone()[0] #(10,)
#     cur.execute('SELECT COUNT(*) FROM players WHERE dead=0 AND role="mafia" ')
#     mafia_alive = cur.fetchone()[0]
#     username_killed = 'никого'
#     if max_votes == mafia_alive:
#         cur.execute('SELECT username FROM players WHERE mafia_vote=?', (max_votes,))
#         username_killed = cur.fetchone()[0]
#         cur.execute('UPDATE players SET dead=1 WHERE username=?', (username_killed,))
#     return username_killed

# @with_db_connection
# def citizen_kill(cur) -> str:
#     cur.execute('SELECT MAX(citizen_vote) FROM players')
#     max_votes = cur.fetchone()[0]
#     cur.execute('SELECT COUNT(*) FROM players WHERE citizen_vote=?', (max_votes,))
#     max_count = cur.fetchone()[0]
#     username_killed = 'никого'
#     if max_count == 1:
#         cur.execute('SELECT username FROM players WHERE citizen_vote=?', (max_votes,))
#         username_killed = cur.fetchone()[0]
#         cur.execute('UPDATE players SET dead=1 WHERE username=?', (username_killed,))
#     return username_killed


@with_db_connection
def vote(cur, type: Literal['mafia_vote', 'citizen_vote'], username: str, player_id: int) -> bool:
    cur.execute("SELECT username FROM players WHERE player_id=? AND dead=0 AND voted=0", (player_id,))
    can_vote = cur.fetchone()
    if can_vote:
        cur.execute(f"UPDATE players SET {type} = {type} + 1 WHERE username=?", (username,))
        cur.execute("UPDATE players SET voted=1 WHERE player_id=?", (player_id,))
        return True
    return False
 
@with_db_connection
def mafia_kill(cur) -> str:
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0] # (10,)
    cur.execute("SELECT COUNT(*) FROM players WHERE dead=0 AND role='mafia' ")
    mafia_alive =cur.fetchone()[0]
    username_killed = "никого"
    if max_votes == mafia_alive:
        cur.execute("SELECT username FROM players WHERE mafia_vote=?", (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
    return username_killed
 
@with_db_connection
def citizen_kill(cur) -> str:
    cur.execute("SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM players WHERE citizen_vote=?", (max_votes,))
    max_count = cur.fetchone()[0]
    username_killed = "никого"
    # if max_count == 1:
    #     cur.execute("SELECT username FROM players WHERE citizen_vote=?", (max_votes,))
    #     username_killed = cur.fetchone()[0]
    #     cur.execute("UPDATE players SET dead=1 WHERE username=?", (username_killed,))
    # return username_killed
    if max_count == 1:
        cur.execute('SELECT username FROM players WHERE citizen_vote=?', (max_votes,))
        username_killed = cur.fetchone()[0]
        cur.execute('UPDATE players SET dead=1 WHERE username=?', (username_killed,))
    return username_killed 

@with_db_connection
def check_winner(cur) -> str | None:
    cur.execute('SELECT COUNT(*) FROM players WHERE role="mafia" and dead=0')
    mafia_alive = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM players WHERE role!="mafia" and dead=0')
    citizen_alive = cur.fetchone()[0]
    if mafia_alive >= citizen_alive:
        return 'Мафия'
    elif mafia_alive == 0:
        return 'Горожане'
    return None

@with_db_connection
def clear(cur, dead: bool=False) -> None:
    sql = 'UPDATE players SET citizen_vote=0, mafia_vote=0, voted=0'
    if dead:
        sql += ', dead=0'
        cur.execute(sql)

if __name__ == '__main__':
    print(check_winner())
    print(clear())
#     print(mafia_kill())
    # create_tables()
    # insert_player(1, 'Артем')
    # insert_player(1, 'Артем')
    # insert_player(2, 'Ефим')
    # insert_player(3, 'Патрик')
    # insert_player(4, 'Рик')
    # insert_player(5, 'Владимир')
    # insert_player(6, 'Кирилл')
    # print(get_all_alive())
    # print(set_roles(players_amount()))
    # print(players_amount())
    # print(get_mafia_usernames())
    # print(get_players_roles())
    # print(vote('mafia_vote', 'Артем', 3))
    # print(vote('mafia_vote', 'Кирилл', 5))
    # print(vote('citizen_vote', 'Рик', 1))
    # print(vote('citizen_vote', 'Ефим', 1))