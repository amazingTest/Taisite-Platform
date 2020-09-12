#! /usr/bin/env python
from app import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5050)