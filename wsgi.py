# import flask app but need to call it "application" for WSGI to work
from ecobidas_ui.app import create_app  # noqa

application = create_app()
