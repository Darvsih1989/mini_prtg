from ui.dashboard import app
from storage.db import init_db
if __name__ == '__main__':
    init_db(reset=True)
    app.run(host='127.0.0.1', port=4731, debug=True)
