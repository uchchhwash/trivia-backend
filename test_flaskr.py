import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', 'postgres', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass

    # Test case for Getting Categories

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    # Test case for Getting Questions by Pagination

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    # Test case for Getting 404 when Pagination Questions Unavailable

    def test_404_get_paginated_questions_unavailable(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Test case for Delete Question by ID

    def test_delete_question(self):
        res = self.client().delete('/questions/58')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # Test case Getting 404 when question is unavailable

    def test_404_delete_question(self):
        res = self.client().delete('/questions/90')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Test case for Add New Question

    def test_post_new_question(self):
        post_data = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # Test case for 404 when Missing Input Provided while Adding New Question

    def test_400_post_new_question(self):
        post_data = {
            'question': 'new question 1',
            'answer': 'new answer 1',
            'category': 1
        }
        res = self.client().post('/questions', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    # Test case for Search Question by String

    def test_search_questions(self):
        post_data = {
            'searchTerm': 'lake',
        }
        res = self.client().post('/search', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_matched_questions"])
        self.assertTrue(len(data["questions"]))

    # Test case for 404 Search Question by String Fails

    def test_404_search_questions(self):
        res = self.client().post('/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource not found")

    # Test case for Get Question for Playing Quiz

    def test_post_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # Test case for 422 when Get Question for Playing Quiz Fails

    def test_422_post_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")


if __name__ == "__main__":
    unittest.main()
