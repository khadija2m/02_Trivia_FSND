import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from flask_migrate import Migrate
from datetime import datetime

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

# Access_Control_Allow
# -----------------------------------
    @app.after_request
    def after_request(response):
        response.headers.add('Access_Control_Allow_Headers', 'Content_Type, Authorization')
        response.headers.add('Access_Control_Allow_Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response



## Pagination:
## --------------------------------------------

    def paginated_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in questions]
        current_questions = questions[start:end]
        return current_questions


## all aavaillable categories:
## --------------------------------------------
    @app.route('/categories')
    def get_categories():
        try:

            categories = Category.query.all()
            category_list = {category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'categories': category_list
            })
        except:
            abort(404)

## Get All questions
## --------------------------------------------


    @app.route('/questions', methods=['GET'])
    def get_questions():

        try:

            questions = Question.query.order_by(Question.id).all()
            questions_list = paginated_questions(request, questions)

            if not questions_list:
                abort(404)

            categories = Category.query.order_by(Category.id).all()
            category_list = {category.id: category.type for category in categories}

            if len(category_list) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': questions_list,
                'total_questions': len(questions),
                'categories': category_list,
                'current_category': None

            })
        except:
            abort(404)

## Delete Question:
## -----------------------------------
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()

            questions = Question.query.order_by(Question.id).all()
            current_question = paginated_questions(request, questions)
            return jsonify({
                'success': True
            })
        except:
            abort(422)


## Post new question:
## -------------------------------------------------
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_question = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'created': None,
                'question': current_question,
                'total_questions': len(current_question)
            })
        except:
            abort(405)

## get questions by categories:
## ------------------------------------
    @app.route('/categories/<int:category_id>/questions')
    def grouped_question(category_id):

        cat_question = []
        questions = Question.query.all()
        current_category = Category.query.filter(Category.id == category_id).one_or_none()
        try:
            for question in questions:
                if question.category == category_id:
                    cat_question.append(question)
            question_pagenate = paginated_questions(request, cat_question)

            return jsonify({
                'success': True,
                'questions': question_pagenate,
                'total_questions':len(cat_question),
                'current_category': current_category.type
            })
        except:
            abort(404)


## Search :
## ---------------------------------------------------
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        searchTerm = body.get('searchTerm', '')

        try:

            if searchTerm is None:
                abore(422)
            questions = Question.query.filter(Question.question.ilike(f'%'+searchTerm+'%')).all()
            if not questions:
                abort(404)


            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': None
            })

        except:
            abort(404)


## Quiz :
## ---------------------------------
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        try:
            category = quiz_category['id']

            if category == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == category).all()

            question_list = [question.format() for question in questions if question.id not in previous_questions]
            if len(question_list) == 0:
                current_question = None
            else:
                current_question = random.choice(question_list)

            return jsonify({
                'success': True,
                'question': current_question
            })

        except:
            abort(422)



## Error Handlers:
## ---------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unproccessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(405)
    def notallowed_method(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method is not allowed'
        }), 405




    return app
