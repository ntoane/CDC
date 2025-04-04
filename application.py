import os
import config
print(os.environ)
# API
from views import create_app

application = create_app()

if __name__ == '__main__':
    
    application.run(debug=True, host="0.0.0.0", port=2002)
