import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # test question
        self.new_question = {
            'answer': 'Test answer',
            'category': 5,
            'difficulty': 5,
            'question': 'Test Question'
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    '''
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    def get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=100', json={'category': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resourse not found')

    '''
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    def test_add_question(self):
        questions_before_addition = len(Question.query.all())
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        questions_after_addition = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(questions_after_addition == questions_before_addition + 1)

    def test_400_empty_add_question(self):
        questions_before_addition = len(Question.query.all())
        empty_question = {
            'answer': '',
            'category': 5,
            'difficulty': 5,
            'question': ''
        }
        res = self.client().post('/questions', json=empty_question)
        data = json.loads(res.data)
        questions_after_addition = len(Question.query.all())

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(questions_after_addition == questions_before_addition)

    '''
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    def test_delete_question(self):
        questions_before_delete = len(Question.query.all())
        question = Question.query.order_by(Question.id.desc()).first()
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        questions_after_delete = len(Question.query.all())
        deleted_question = Question.query.filter(Question.id == question.id).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question.id))
        self.assertTrue(questions_after_delete == questions_before_delete - 1)
        self.assertEqual(deleted_question, None)

    '''
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    ''' 
    def test_search(self):
        search_term = {'searchTerm': 'title'}
        res = self.client().post('/questions/results', json=search_term)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    '''
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    
    def test_get_questions_by_category(self):
        
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(data["current_category"])
        self.assertTrue(len(data["questions"]))

    '''
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    
    def test_play_quiz(self):
        body = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
        res = self.client().post('/quizzes', json=body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        #self.assertTrue()
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()