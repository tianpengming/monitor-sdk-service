from conf import settings
import json
import logging
logger = logging.getLogger()

class Status400(Exception):
    pass

class Status403(Exception):
    pass

def except_handler(message=None):
    def decrorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                forward = self.request.headers.get("X-Forwarded-For", None)
                if forward:
                    self.request.remote_ip = forward.split(",")[0].strip()
                if self.request.body:
                    req_data = json.loads(self.request.body)
                else:
                    req_data = self.request.arguments
                ret = func(self, req_data, *args, **kwargs)
                self.write(ret)
            except Status400 as e:
                logger.debug(e.message)
                self.set_status(400)
                self.write({'return':-1, 'message':e.message})
            except Status403 as e:
                logger.debug(e.message)
                self.set_status(403)
                self.write({'return':-1, 'message':e.message})
            except Exception as e:
                logger.debug(e.message)
                if settings.opt['DEBUG']:
                    import traceback
                    traceback.print_exc()
                self.set_status(500)
                if 'message' not in locals().keys():
                    message = e.message
                else:
                    if message is None:
                        message = e.message
                self.write({'return': -1, 'message': e.message})
            finally:
                logger.info('[request parameter]: {0}'.format(self.request.arguments))
                logger.info('[request body]: {0}'.format(self.request.body))
        return wrapper
    return decrorator
