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
  cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

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
    
  #Create a POST endpoint to get questions based on a search term. 
  @app.route('/questions/results', methods=['POST'])
  def search_results():
    search_term = request.get_json()['searchTerm']
    search = '%{}%'.format(search_term)
    questions = Question.query.filter(Question.question.ilike(search)).all()
    total_questions = len(questions)
    current_questions = paginate_questions(request, questions)
    if questions:
      print(questions)
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
  
  #Create a POST endpoint to get questions to play the quiz.
  @app.route('/quizzes', methods=['POST'])
  def play_trivia():
    body = request.get_json()
    category_id = body.get('quiz_category').get('id')
    previous_questions = body.get('previous_questions')

    if not category_id:
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

  #Create error handlers for all expected errors 
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
          'message': 'unprocessable'
      }), 422
 
  return app

    