import sys
import traceback
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException

class ErrorHandler:
    def __init__(self, app, debug_mode=False):
        self.app = app
        self.debug_mode = debug_mode
        self.register_error_handlers()

    def register_error_handlers(self):
        @self.app.errorhandler(Exception)
        def handle_exception(error):
            if isinstance(error, HTTPException):
                return self.handle_http_error(error)
            return self.handle_generic_error(error)

    def handle_http_error(self, error):
        if self.debug_mode:
            error_info = {
                'code': error.code,
                'name': error.name,
                'description': error.description,
            }
        else:
            error_info = {
                'code': error.code,
                'message': 'An error occurred. Please try again later.'
            }

        if request.is_json:
            return jsonify(error_info), error.code
        return render_template('error.html', error=error_info), error.code

    def handle_generic_error(self, error):
        # Log the full error for debugging
        exc_info = sys.exc_info()
        self.app.logger.error(''.join(traceback.format_exception(*exc_info)))

        if self.debug_mode:
            error_info = {
                'type': error.__class__.__name__,
                'message': str(error),
                'traceback': traceback.format_exc()
            }
        else:
            error_info = {
                'message': 'An unexpected error occurred. Please try again later.'
            }

        if request.is_json:
            return jsonify("error_info"), 500
        return render_template('error.html', error=error_info), 500
