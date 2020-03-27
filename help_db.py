import psycopg2
import os

class DBHelper:
    def __init__(self, db_name='posts_list'):
        self.db_name =  db_name
        self.username = 'postgres'
        self.password = 'pass'
        self.hostname = '127.0.0.1'
        self.port = url.port

        try:
            self.conn = psycopg2.connect(database=self.db_name,
            user = self.username,
            password = self.password,
            host = self.hostname,
            port = self.port)
            
            self.cur = self.conn.cursor()
        except Exception as ex:
            print(ex)


    def __enter__(self):
        self._setup()
        return self


    def __exit__(self, type, value, traceback):
        self.close()


    def _setup(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS posts_list("
                        "post_id SERIAL PRIMARY KEY NOT NULL UNIQUE,"
                        "post_link TEXT NOT NULL DEFAULT 'https://t.me/it_virologist',"
                        "post_topic TEXT);")

        self.cur.execute("CREATE TABLE IF NOT EXISTS user_list("
                        "user_id INTEGER PRIMARY KEY NOT NULL,"
                        "state_in_topics INTEGER DEFAULT 4,"
                        "state_in_links INTEGER DEFAULT 0,"
                        "enter_topic TEXT NOT NULL DEFAULT 'nill');")

        self.conn.commit()


    def close(self):
        self.cur.close()
        self.conn.close()



    def check_user(self, user_id):
        query = f'SELECT count(*) FROM user_list WHERE user_id = {user_id}'
        self.cur.execute(query)
        if self.cur.fetchone()[0] != 0:
            return True


    def add_user(self, user_id):
        if not self.check_user(user_id):
            query = f'INSERT INTO user_list (user_id) VALUES ({user_id})'
            self.cur.execute(query)
            self.conn.commit()


    def set_user_state_topics(self, user_id, state):
        if self.check_user(user_id):
            query = f'UPDATE user_list SET state_in_topics = {state} WHERE user_id = {user_id}'
            self.cur.execute(query)
            self.conn.commit()


    def set_user_state_links(self, user_id, state):
        if self.check_user(user_id):
            query = f'UPDATE user_list SET state_in_links = {state} WHERE user_id = {user_id}'
            self.cur.execute(query)
            self.conn.commit()

    
    def update_user_enter_topic(self, user_id, state):
        if self.check_user(user_id):
            query = f"UPDATE user_list SET enter_topic = '{state}' WHERE user_id = {user_id}"
            self.cur.execute(query)
            self.conn.commit()


    def get_user_enter_topic(self, user_id):
        if self.check_user(user_id):
            query = f'SELECT enter_topic FROM user_list WHERE user_id = {user_id}'
            self.cur.execute(query)
            return self.cur.fetchone()[0]


    def get_user_state_topics(self, user_id):
        if self.check_user(user_id):
            query = f'SELECT state_in_topics FROM user_list WHERE user_id = {user_id}'
            self.cur.execute(query)
            return self.cur.fetchone()[0]


    def get_user_state_links(self, user_id):
        if self.check_user(user_id):
            query = f'SELECT state_in_links FROM user_list WHERE user_id = {user_id}'
            self.cur.execute(query)
            return self.cur.fetchone()[0]
    

    #POSTS_LIST

    def check_post(self, post_link):
        query = f"SELECT post_id from posts_list WHERE post_link = '{post_link}'"
        self.cur.execute(query)
        if len(self.cur.fetchall()) != 0:
            return True


    def check_topic(self, post_topic):
        query = f"SELECT post_id FROM posts_list WHERE post_topic = '{post_topic}'"
        self.cur.execute(query)
        if len(self.cur.fetchall()) != 0:
            return True
       

    def set_post(self, post_link, post_topic):
        query = f"INSERT INTO posts_list (post_link, post_topic) VALUES ('{post_link}', '{post_topic}')"
        self.cur.execute(query)
        self.conn.commit()
        return 'ok'
    
    
    def update_post_topic(self, post_link, old_topic, new_topic):
        if self.check_post(post_link):
            query = f"UPDATE posts_list SET post_topic = '{new_topic}' WHERE post_link LIKE '{post_link}' AND post_topic LIKE '{old_topic}'"
            self.cur.execute(query)
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed update! It seems that such a link is not in database...'
    

    def update_post_link(self, post_link, new_link):
        if self.check_post(post_link):
            query = f"UPDATE posts_list SET post_link = '{new_link}' WHERE post_link = '{post_link}'"
            self.cur.execute(query)
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed update! It seems that such a link is not in database...'
    
    
    def get_post_topics(self):
        query = 'SELECT DISTINCT post_topic FROM posts_list'
        self.cur.execute(query)
        result = [state[0] for state in self.cur.fetchall()]
        return result


    def get_topic_links(self, post_topic):
        if self.check_topic(post_topic):
            query = f"SELECT post_link FROM posts_list WHERE post_topic = '{post_topic}'"
            self.cur.execute(query)
            result = [state[0] for state in self.cur.fetchall()]
            return result
    
    
    def del_post_link(self, post_link):
        if self.check_post(post_link):
            query = f"DELETE FROM posts_list WHERE post_link='{post_link}'"
            self.cur.execute(query)
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed delete! It seems that such a link is not in database...'
