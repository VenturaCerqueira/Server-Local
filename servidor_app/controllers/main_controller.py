# servidor_app/controllers/main_controller.py
from flask import (
    Blueprint, render_template, current_app, send_from_directory, 
    send_file, request, jsonify
)
from werkzeug.utils import secure_filename
from servidor_app.models.file_system_model import FileSystemModel
from servidor_app.services.server_info_service import get_server_info
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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
def browse_path(sub_path):
    try:
        fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
        server_data = get_server_info(current_app.config['ROOT_DIR'])
        pastas, current_path, parent_path = fs_model.list_directory(sub_path)
        return render_template('index.html', 
                               dados_servidor=server_data, 
                               pastas=pastas, 
                               current_path=current_path,
                               parent_path=parent_path)
    except FileNotFoundError:
        return "Diretório não encontrado", 404
    except PermissionError as e:
        return f"Acesso Negado: {e}", 403
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