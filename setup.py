""" To start the web server """
from conferenceapp import app

if __name__=='__main__':
    app.run(debug=True,port=8080)
