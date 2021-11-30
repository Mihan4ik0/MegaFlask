from app import app, db
from app.models import User, Post


@app.shell_context_processor  # контекст оболочки
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


if __name__=='__main__':  # проверка запуска на зависимость
    app.run()
