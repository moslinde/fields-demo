###############################################################################
#                            RUN MAIN
#
# Main call for initiate the program
###############################################################################

from application.dash_fields import app
from settings import config



app.run_server(debug=config.debug, host=config.host, port=config.port)