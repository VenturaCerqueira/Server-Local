from flask import (
    Blueprint, render_template, current_app, send_from_directory,
    send_file, request, jsonify, redirect, url_for, flash
)
from werkzeug.utils import secure_filename
from servidor_app.models.file_system_model import FileSystemModel
from servidor_app.services.server_info_service import get_server_info
from flask_login import login_user, logout_user, login_required, current_user
import os

from servidor_app.models.user_model import users

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users.get(username)

        if user and user.check_password(password):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Nome de usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('main.login'))

# Adicionar @login_required para proteger as rotas
@main_bp.route('/')
@login_required 
def index():
    try:
        fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
        server_data = get_server_info(current_app.config['ROOT_DIR'])
        pastas, current_path, parent_path = fs_model.list_directory()
        return render_template('index.html', 
                               dados_servidor=server_data, 
                               pastas=pastas, 
                               current_path=current_path, 
                               parent_path=parent_path)
    except Exception as e:
        return f"Erro ao acessar o diretório raiz: {e}", 500

@main_bp.route('/browse/<path:sub_path>')
@login_required
def browse_path(sub_path):
    try:
        fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
        pastas, current_path, parent_path = fs_model.list_directory(sub_path)
        server_data = get_server_info(current_app.config['ROOT_DIR'], sub_path)
        return render_template('index.html', 
                               dados_servidor=server_data, 
                               pastas=pastas, 
                               current_path=current_path, 
                               parent_path=parent_path)
    except FileNotFoundError:
        return "Diretório não encontrado", 404
    except Exception as e:
        return f"Erro ao acessar o diretório: {e}", 500


@main_bp.route('/download/<path:file_path>')
def download_file(file_path):
    fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
    full_path = os.path.join(fs_model.root_dir, file_path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(fs_model.root_dir)):
        return "Acesso negado", 403
    if os.path.isfile(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=True)
    elif os.path.isdir(full_path):
        memory_file, download_name = fs_model.create_zip_from_folder(file_path)
        return send_file(memory_file, download_name=download_name, as_attachment=True, mimetype='application/zip')
    else:
        return "Caminho não encontrado", 404

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        current_path = request.form.get('current_path', '')
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'message': 'Nome do arquivo vazio'}), 400
        
        if file:
            fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
            filename = fs_model.save_file(file, current_path)
            return jsonify({
                'success': True, 
                'message': f'Arquivo "{filename}" enviado com sucesso.',
                'filename': filename,
                'redirect_url': f'/browse/{current_path}' if current_path else '/'
            }), 201

    except PermissionError:
        return jsonify({'success': False, 'message': 'Permissão negada para salvar o arquivo'}), 403
    except Exception as e:
        current_app.logger.error(f"Erro ao fazer upload do arquivo: {e}")
        return jsonify({'success': False, 'message': f'Ocorreu um erro interno: {str(e)}'}), 500

# Nova rota para criar pastas
@main_bp.route('/create_folder', methods=['POST'])
def create_folder():
    try:
        data = request.get_json()
        folder_name = data.get('folder_name')
        current_path = data.get('current_path', '')

        if not folder_name:
            return jsonify({'success': False, 'message': 'O nome da pasta não pode estar vazio.'}), 400
        
        fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
        fs_model.create_folder(folder_name, current_path)
        
        redirect_url = f'/browse/{current_path}' if current_path else '/'
        return jsonify({'success': True, 'message': f'Pasta "{folder_name}" criada com sucesso.', 'redirect_url': redirect_url}), 201

    except PermissionError:
        return jsonify({'success': False, 'message': 'Permissão negada para criar a pasta.'}), 403
    except FileExistsError:
        return jsonify({'success': False, 'message': 'Uma pasta ou arquivo com esse nome já existe.'}), 409
    except Exception as e:
        current_app.logger.error(f"Erro ao criar a pasta: {e}")
        return jsonify({'success': False, 'message': f'Ocorreu um erro interno: {str(e)}'}), 500