import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

@app.route('/users', methods=['GET']) #Rota para receber todos os usuarios da tabela users
def get_users():

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users;')
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    users_list = [{'id': user[0], 'name': user[1], 'email': user[2]} for user in users]
    return jsonify(users_list)

@app.route('/users/<int:user_id>', methods=['GET']) #Rota para obter um usuário específico por ID.
def get_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        abort(404, description='User not found')
    
    user_data = {'id': user[0], 'name': user[1], 'email': user[2]}
    return jsonify(user_data)

@app.route('/users', methods=['POST'])
def create_user():
    
    if not request.json or not all(k in request.json for k in ['name', 'email']):
        abort(400, description='Invalid input')

    new_name = request.json['name']
    new_email = request.json['email']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id',
        (new_name, new_email)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'id': new_id, 'name': new_name, 'email': new_email}), 201

@app.route('/users/<int:user_id>', methods=['PUT']) #Rota para atualizar um usuário existente
def update_user(user_id):

    if not request.json or not any(k in request.json for k in ['name', 'email']):
        abort(400, description='Invalid input')

    new_name = request.json.get('name')
    new_email = request.json.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET name = %s, email = %s WHERE id = %s',
        (new_name, new_email, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        abort(404, description='User not found')
    
    return jsonify({'id': user_id, 'name': new_name, 'email': new_email})

@app.route('/users/<int:user_id>', methods=['DELETE']) #Rota usada para deletar um usuário por ID.
def delete_user(user_id):

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = %s', (user_id))
    conn.commit()
    cursor.close()
    conn.close()

    if cursor.rowcount == 0:
        abort(404, description='User not foud')

    return jsonify({'result': 'User deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
