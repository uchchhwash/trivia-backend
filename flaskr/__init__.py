import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import re
from models import setup_db, Question, Category

# variable for configuring pagination limit
QUESTIONS_PER_PAGE = 10

# funtions for paginating the questions


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

    # CORS Setup for allowing all Origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # after request decorator for Access Control Allow

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response


# API for Getting All Categories

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = list(map(Category.format, Category.query.all()))
        return jsonify({
            "success": True,
            "categories": categories,
            "total_categories": len(categories)
        })

    # API for Getting All Questions By Pagination

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

    # API for DELETE Question By ID
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

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

    # API for Add New Question
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        valid_flag = [new_question, new_answer, new_category, new_difficulty]
        if all(valid_flag) is False:
            abort(400)

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)
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

    # API for Search for a Question by String
    @app.route('/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search = body.get('searchTerm', None)
            if search is not None:
                questions = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search)))
                questions = [question.format() for question in questions.all()]
                return jsonify({
                    "success": True,
                    "questions": questions,
                    "total_matched_questions": len(questions)
                })
            else:
                abort(422)
        except:
            abort(404)

    # API for Get Questions by category
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter(
                Question.category == category_id).order_by(Question.id).all()
            questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": questions,
                "total_questions": len(questions),
                "current_category": category_id
            })
        except:
            abort(404)

    # API for Get Question to play the quiz.

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
                    selections = Question.query.filter(
                        Question.category == quiz_category['id']).all()

                question_set = [question.format() for question in selections
                                if question.id not in previous_questions]

                if len(question_set) == 0:
                    return jsonify({
                        "success": True,
                        "question": None
                    })
                question = random.choice(question_set)
                return jsonify({
                    "success": True,
                    "question": question
                })
        except:
            abort(422)

    # ALL Error Handlers

    # 404 Resource non Found
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    # 422 Unprocessable
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    # 400 Bad Request
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    # 500 Internal server error
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        })

    return app
