import sqlite3

class DBHelper:
    def __init__(self, db_name = 'posts_list.sqlite'):
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(self.db_name)
        except Exception as ex:
            print(ex)


    def __enter__(self):
        self._setup()
        return self


    def __exit__(self, type, value, traceback):
        self.close()


    def _setup(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS posts_list('
                        'post_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,'
                        'post_link TEXT NOT NULL DEFAULT "https://t.me/it_virologist",'
                        'post_topic TEXT);')

        self.conn.execute('CREATE TABLE IF NOT EXISTS user_list('
                        'user_id INTEGER PRIMARY KEY NOT NULL,'
                        'state_in_topics INTEGER DEFAULT (4),'
                        'state_in_links INTEGER DEFAULT 0,'
                        'enter_topic TEXT NOT NULL DEFAULT "nill");')

        self.conn.commit()


    def close(self):
        self.conn.close()
    
    
    #USER_LIST

    def check_user(self, user_id):
        if len([state[0] for state in self.conn.execute('SELECT user_id FROM user_list WHERE user_id = (?)', (user_id,))]):
            return True


    def add_user(self, user_id):
        if not self.check_user(user_id):
            self.conn.execute('INSERT INTO user_list (user_id) VALUES (?)', (user_id,))
            self.conn.commit()


    def set_user_state_topics(self, user_id, state):
        if self.check_user(user_id):
            self.conn.execute('UPDATE user_list SET state_in_topics = (?) WHERE user_id = (?)', (state, user_id))
            self.conn.commit()


    def set_user_state_links(self, user_id, state):
        if self.check_user(user_id):
            self.conn.execute('UPDATE user_list SET state_in_links = (?) WHERE user_id = (?)', (state, user_id))
            self.conn.commit()

    
    def update_user_enter_topic(self, user_id, state):
        if self.check_user(user_id):
            self.conn.execute('UPDATE user_list SET enter_topic = (?) WHERE user_id = (?)', (state, user_id))
            self.conn.commit()


    def get_user_enter_topic(self, user_id):
        if self.check_user(user_id):
            topic = self.conn.execute('SELECT enter_topic FROM user_list WHERE user_id = (?)', (user_id,))
            return topic.fetchone()[0]


    def get_user_state_topics(self, user_id):
        if self.check_user(user_id):
            state = self.conn.execute('SELECT state_in_topics FROM user_list WHERE user_id = (?)', (user_id,))
            return state.fetchone()[0]


    def get_user_state_links(self, user_id):
        if self.check_user(user_id):
            state = self.conn.execute('SELECT state_in_links FROM user_list WHERE user_id = (?)', (user_id,))
            return state.fetchone()[0]
    

    #POSTS_LIST

    def check_post(self, post_link):
        if len([state[0] for state in self.conn.execute('SELECT post_id from posts_list WHERE post_link = (?)', (post_link,))]):
            return True


    def check_topic(self, post_topic):
        if len([state[0] for state in self.conn.execute('SELECT post_id FROM posts_list WHERE post_topic = (?)', (post_topic,))]):
            return True
       

    def set_post(self, post_link, post_topic):
        if not self.check_post(post_link):
            self.conn.execute('INSERT INTO posts_list VALUES (null, ?, ?)', (post_link, post_topic))
            self.conn.commit()
            return 'ok'
        else:
            return 'this link is already exists...'
    
    
    def update_post_topic(self, post_link, new_topic):
        if self.check_post(post_link):
            self.conn.execute('UPDATE posts_list SET post_topic = (?) WHERE post_link = (?)', (new_topic, post_link))
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed update! It seems that such a link is not in database...'
    

    def update_post_link(self, post_link, new_link):
        if self.check_post(post_link):
            self.conn.execute('UPDATE posts_list SET post_link = (?) WHERE post_link = (?)', (new_link, post_link))
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed update! It seems that such a link is not in database...'
    
    
    def get_post_topics(self):
        result = [state[0] for state in self.conn.execute('SELECT DISTINCT post_topic FROM posts_list')]
        return result


    def get_topic_links(self, post_topic):
        if self.check_topic(post_topic):
            result = [state[0] for state in self.conn.execute('SELECT post_link FROM posts_list WHERE post_topic = (?)', (post_topic,))]
            return result
    
    
    def del_post_link(self, post_link):
        if self.check_post(post_link):
            self.conn.execute('DELETE FROM posts_list WHERE post_link=(?)', (post_link,))
            self.conn.commit()
            return 'ok'
        else:
            return 'Failed delete! It seems that such a link is not in database...'
        
if __name__ == "__main__":
    with DBHelper() as db:
        pass