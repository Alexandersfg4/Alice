import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def create_question_table(self):
        #create a table questions
        with self.connection:
            return self.cursor.execute('''CREATE TABLE "questions" ("id"	INTEGER UNIQUE, "question"	TEXT UNIQUE, PRIMARY KEY("id" AUTOINCREMENT))''')
        # create a table users
    def create_users_table(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('''CREATE TABLE "users" ("id"	INTEGER UNIQUE, "user_id" INTEGER UNIQUE, "number_of_the_question" INTEGER, PRIMARY KEY("id" AUTOINCREMENT))''')

        #insert question
    def insert_questions(self, question):
        with self.connection:
            return self.cursor.execute(f'INSERT INTO questions (question) VALUES ("{question}")')

        #reset user progress
    def delete_user_data(self, user_id):
        with self.connection:
            return self.cursor.execute(f'UPDATE users SET number_of_the_question = 1  WHERE user_id = ("{user_id}")')


    def check_user_state(self, user_id):
        with self.connection:
                return self.cursor.execute(f'SELECT number_of_the_question FROM users WHERE user_id = ("{user_id}")').fetchone()

        #add new user
    def add_new_user(self, user_id):
        with self.connection:
            return self.cursor.execute(f'INSERT INTO users (user_id, number_of_the_question) VALUES ("{user_id}", 1)')

        #change state
    def change_state(self, new_number_of_the_question, user_id):
        with self.connection:
                return self.cursor.execute(f'UPDATE users SET number_of_the_question = "{new_number_of_the_question}"  WHERE user_id = ("{user_id}")')

    def get_question(self, number_of_the_question):
        return self.cursor.execute(f'SELECT question FROM questions WHERE id = ("{number_of_the_question}")').fetchone()

        #close db
    def close(self):
        self.connection.close()


if __name__ == '__main__':
    db = SQLighter('test.db')
    db.close()