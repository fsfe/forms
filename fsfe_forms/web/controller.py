import redis
from bottle import route, request, redirect, abort
from fsfe_forms.common import exceptions
from fsfe_forms.common.models import SendData
from fsfe_forms.common.services import SenderService


def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.BadRequest as e:
            abort(400, e.message)
        except exceptions.NotFound as e:
            abort(404, e.message)
        except redis.exceptions.ConnectionError as e:
            abort(500, 'Database connection failed')

    return wrapper


def id_extractor(id_name, method):
    def decorator(function):
        def wrapper(*args, **kwargs):
            _id = getattr(request, method).get(id_name)
            if _id:
                return function(_id, *args, **kwargs)
            raise exceptions.BadRequest
        return wrapper
    return decorator


@route('/email', method='GET')
@error_handler
@id_extractor('appid', 'GET')
def email_get(appid):
    send_data = SendData.from_request(appid, request.GET, request.url)
    config = SenderService.validate_and_send_email(send_data)
    return redirect(config.redirect)


@route('/email', method='POST')
@error_handler
@id_extractor('appid', 'POST')
def email_post(appid):
    send_data = SendData.from_request(appid, request.forms, request.url)
    config = SenderService.validate_and_send_email(send_data)
    return redirect(config.redirect)


@route('/confirm', method='GET')
@error_handler
@id_extractor('id', 'GET')
def confirmation(id):
    config = SenderService.confirm_email(id)
    return redirect(config.redirect_confirmed or config.redirect)
