# run.py
from servidor_app import create_app

app = create_app()

if __name__ == '__main__':
    # O modo debug não deve ser usado em produção
    app.run(debug=True, port=5000)