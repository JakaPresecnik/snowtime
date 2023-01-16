from flask import jsonify
from auth import AuthError

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#  oooooooooooo                                               
#  `888'     `8                                               
#   888         oooo d8b oooo d8b  .ooooo.  oooo d8b  .oooo.o 
#   888oooo8    `888""8P `888""8P d88' `88b `888""8P d88(  "8 
#   888    "     888      888     888   888  888     `"Y88b.  
#   888       o  888      888     888   888  888     o.  )88b 
#  o888ooooood8 d888b    d888b    `Y8bod8P' d888b    8""888P' 
                                                           

def errors(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({
            'success': False,
            'error': 409,
            'message': 'Conflict. Already Exists'
        }), 409

    @app.errorhandler(422)
    def unprocassable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    @app.errorhandler(AuthError)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code