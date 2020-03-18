import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import unittest

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]
  

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  #Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  #Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response
  
  #Create an endpoint to handle GET requests for all available categories.
  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    categories_dict = {category.id: category.type for category in categories}
    return jsonify({
      'success': True,
      'categories': categories_dict,
      'Total categories': len(categories_dict)
    })

  #Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). 

  @app.route('/questions')
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    total_questions = len(questions)
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.all()
    categories_dict = {category.id: category.type for category in categories}
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'categories': categories_dict,
      'current_category': None
    })
  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  #Create an endpoint to DELETE question using a question ID. 
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)
    try:
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id,

      })
    except:
      abort(422)


  '''
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  #Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
  @app.route('/questions', methods=['POST'])
  def add_question():
    question = request.get_json()
    if not question['question'] or not question['answer']:
      abort(400)
    new_question = Question(
      question = question.get('question'),
      answer = question.get('answer'),
      difficulty = question.get('difficulty'),
      category = question.get('category')
    )
    try:
      Question.insert(new_question)
      return jsonify({
        'question': question,
        'success': True,
      })
    except:
      abort(422)
    


  
  '''
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  
  #Create a POST endpoint to get questions based on a search term. 
  @app.route('/questions/results', methods=['POST'])
  def search_results():
    search_term = request.get_json()['searchTerm']
    search = "%{}%".format(search_term)
    questions = Question.query.filter(Question.question.ilike(search)).all()
    total_questions = len(questions)
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    categories = Category.query.all()
    categories_dict = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'categories': categories_dict,
      'current_category': None
    })



  '''
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  ''' 
  
  #Create a GET endpoint to get questions based on category. 
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    total_questions = len(questions)
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    category = Category.query.filter(Category.id == category_id).one_or_none()
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': total_questions,
      'current_category': category.type,
    })
  
  '''
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_trivia():
    body = request.get_json()
    category_id = body.get('quiz_category').get('id')
    previous_questions = body.get('previous_questions')

    if category_id == 0:
      questions = Question.query.order_by(Question.id).all()
    else:
      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()

    if len(previous_questions) == len(questions):
      return jsonify({
        'success': True,
      })

    question = random.choice(questions)

    while question.id in previous_questions:
        question = random.choice(questions)

    print(question.answer)
    return jsonify({
      'success': True,
      'question': question.format(),
    })

  '''
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'resourse not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': 'Unprocessable'
      }), 422

  
  return app

    