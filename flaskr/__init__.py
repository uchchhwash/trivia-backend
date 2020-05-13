import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import re
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  currrent_page_questions = questions[start:end]
  return currrent_page_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def get_categories():
    categories = list(map(Category.format, Category.query.all()))
    return jsonify({
      "success": True,
      "categories": categories,
      "total_categories": len(categories)
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  
  '''
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    current_page_questions = paginate_questions(request, questions)
    categories = list(map(Category.format, Category.query.all()))
    if len(current_page_questions) == 0:
      abort(404)
    return jsonify({
      "success": True,
      "questions": current_page_questions,
      "total_questions": len(Question.query.all()),
      "categories": categories,
      "current_category": None
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)
      
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = [question.format() for question in selection]

      return jsonify({
        "success": True,
        "deleted": question_id,
        "questions": current_questions,
        "total_questions": len(Question.query.all())
      })

    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions',methods=['POST'])
  def add_question():
    body = request.get_json()
    print(body)
    new_question =  body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)

    try:
      question = Question(question=new_question, answer=new_answer, category= new_category, difficulty=new_difficulty) 
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_page_questions = paginate_questions(request, selection)

      return jsonify({
        "success": True,
        "created": question.id,
        "questions": current_page_questions,
        "total_quesitons": len(Question.query.all())
      })

    except:
      abort(500) 
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search = body.get('searchTerm', None)
    try:
      if search:
        questions =  Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        questions = [question.format() for question in questions.all()]
        return jsonify({
            "questions": questions ,
            "total_matched_questions": len(questions)
        })
      else:
        abort(404)
    except:
      abort(404)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
      questions = [question.format() for question in questions]

      return jsonify({
        "success": True,
        "questions": questions,
        "total_questions":len(questions),
        "current_category":category_id
      })
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz_quesitons():
    body = request.get_json()
    
    previous_questions = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)
    selection = []
    
    try:
      if quiz_category is not None:
        if quiz_category['id'] == 0:
          selections = Question.query.all()
        else:
          selections = Question.query.filter(Question.category == quiz_category['id']).all()
          
        question_set = [question.format() for question in selections 
                      if question.id not in previous_questions]
      
        if len(question_set) == 0:
          return jsonify({
            "success": True,
            "question": None
          })
        question = random.choice(question_set)
        print(question)
        return jsonify({
            "success": True,
            "question": question
        })
    except:
      abort(500)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400

  @app.errorhandler(500)
  def internal_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal server error"
      })

  return app

    