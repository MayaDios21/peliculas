import os
import environ
import requests
import psycopg2
from  datetime import datetime, date, timezone 
import sys
import time


def add_movie(movie_id):
    env = environ.Env()
    environ.Env.read_env('../.env')
    print('API_KEY: ', env('API_KEY'))
    print('API_TOKEN: ', env('API_TOKEN'))

    '''
    url --request GET \
         --url 'https://api.themoviedb.org/3/movie/76341?language=en-US' \
         --header 'Authorization: Aasdfqwer' \
         --header 'accept: application/json'
    '''
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {env('API_TOKEN')}"}



    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?language=en-US', headers=headers) 
    print(r.json())
    m = r.json()

    conn = psycopg2.connect(dbname='django', host='/tmp')
    cur = conn.cursor()

    sql = 'SELECT * FROM movies_movie WHERE title = %s'
    cur.execute(sql, (m['title'],))
    movie_exists = cur.fetchall()

    print(movie_exists)

    r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US', headers=headers) 
    credits = r.json()


    actors = [( actor['name'], actor['known_for_department']) for actor in credits['cast'][:10]] 
    crew =   [(   job['name'], job['job']) for job in credits['crew'][:15]]

    credits_list = actors + crew




    jobs = [job for person, job in credits_list]
    jobs = set(jobs)
    print(jobs)

    sql = 'SELECT * FROM movies_job WHERE name IN %s'
    cur.execute(sql, (tuple(jobs),))
    jobs_in_db = cur.fetchall()

    jobs_to_create = [(name,) for name in jobs if name not in [row[1] for row in jobs_in_db]]    
    sql = 'INSERT INTO movies_job (name) values  (%s)'
    cur.executemany(sql, jobs_to_create) 

    # Procesar personas
    persons = [person for person, job in credits_list]
    persons = set(persons)
    print(persons)
    sql = 'SELECT * FROM movies_person WHERE name IN %s'
    cur.execute(sql, (tuple(persons),))
    persons_in_db = cur.fetchall()

    persons_to_create = [(name,) for name in persons if name not in [row[1] for row in persons_in_db]]    
    sql = 'INSERT INTO movies_person (name) values  (%s)'
    cur.executemany(sql, persons_to_create) 

    # Procesar géneros
    genres = [d['name'] for d in m['genres']] 
    print(genres)

    sql = 'SELECT * FROM movies_genre WHERE name IN %s'
    cur.execute(sql, (tuple(genres),))
    genres_in_db = cur.fetchall()

    genres_to_create = [(name,) for name in genres if name not in [row[1] for row in genres_in_db]]
    sql = 'INSERT INTO movies_genre (name) values  (%s)'
    cur.executemany(sql, genres_to_create) 

    # Insertar película
    date_obj = date.fromisoformat(m['release_date']) 
    date_time = datetime.combine(date_obj, datetime.min.time())

    sql = '''INSERT INTO movies_movie 
             (title,
              overview,
              release_date,
              running_time,
              budget,
              tmdb_id,
              revenue,
              poster_path) values  (%s, %s, %s, %s, %s, %s, %s, %s);'''

    movie_tuple = (m['title'], m['overview'], date_time.astimezone(timezone.utc), m['runtime'], 
                   m['budget'], movie_id, m['revenue'], m['poster_path'])
    print(movie_tuple)
    cur.execute(sql, movie_tuple)

    # Asociar géneros con película
    sql = '''INSERT INTO movies_movie_genres (movie_id, genre_id)
             SELECT (SELECT id FROM movies_movie WHERE title = %s) as movie_id, id as genre_id 
             FROM movies_genre 
             WHERE name IN %s'''
    cur.execute(sql, (m['title'], tuple(genres),))

    # Asociar créditos (actores/directores) con película
    print(credits_list)
    for credit in credits_list:
        sql = '''INSERT INTO movies_moviecredit (movie_id, person_id, job_id)
                 SELECT id,
                 (SELECT id FROM movies_person WHERE name = %s) as person_id,
                 (SELECT id FROM movies_job WHERE name = %s) as job_id
                 FROM movies_movie 
                 WHERE title = %s'''
        cur.execute(sql, (credit[0], credit[1], m['title'],))

    conn.commit()
    print(f"  -> ¡Éxito! Guardada: '{m['title']}'")


# 2. La nueva función que lee el archivo txt
def load_movies_from_txt(filename="mis_ids.txt"):
    # Verificamos que el archivo exista
    if not os.path.exists(filename):
        print(f"Error: No se encontró el archivo '{filename}'.")
        return

    # Leemos el archivo y limpiamos los espacios o saltos de línea
    with open(filename, 'r') as file:
        # Extraemos solo los números, ignorando líneas vacías
        movie_ids = [line.strip() for line in file if line.strip().isdigit()]

    print(f"\nSe encontraron {len(movie_ids)} IDs de películas en {filename}.\n")

    # Recorremos la lista y descargamos una por una
    for index, m_id in enumerate(movie_ids, 1):
        print(f"[{index}/{len(movie_ids)}] Procesando TMDB ID: {m_id}...")
        try:
            add_movie(int(m_id))
            # ⏱️ PAUSA DE MEDIO SEGUNDO (Evita que la API te bloquee por SPAM)
            time.sleep(0.5) 
        except Exception as e:
            print(f"  -> Error inesperado con el ID {m_id}: {e}")

    print("\n¡Proceso finalizado con éxito!")


if __name__ == "__main__":
    # Si pasas un argumento, carga esa película específica
    # Si no, carga todas las del archivo mis_ids.txt
    if len(sys.argv) > 1:
        add_movie(int(sys.argv[1]))
    else:
        load_movies_from_txt("mis_ids.txt")


