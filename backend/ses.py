import cherrypy
import mine

if __name__ == '__main__':

    def cors():
        if cherrypy.request.method == 'OPTIONS':
            print('hi')
            # preflign request
            # see http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0
            cherrypy.response.headers['Access-Control-Allow-Methods'] = 'POST'
            cherrypy.response.headers['Access-Control-Allow-Headers'] = 'content-type'
            cherrypy.response.headers['Access-Control-Allow-Origin'] = 'http://0.0.0.0:3000/'
            cherrypy.response.headers['Access-Control-Allow-Credentials'] = False
            print(cherrypy.response)
            # tell CherryPy no avoid normal handler
            return True
        else:
            cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

    conf = {
        '/': {
            'tools.sessions.on': True,

        }
    }

    cherrypy.tools.cors = cherrypy._cptools.HandlerTool(cors)
    cherrypy.quickstart(mine.MineApp(), '/', conf)
