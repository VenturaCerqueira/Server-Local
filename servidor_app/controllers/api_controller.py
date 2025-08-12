# servidor_app/controllers/api_controller.py
from flask import Blueprint, jsonify, current_app, request
from servidor_app.models.file_system_model import FileSystemModel
from servidor_app.services.server_info_service import get_server_info
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/status')
def api_status():
    server_data = get_server_info(current_app.config['ROOT_DIR'])
    return jsonify(server_data)

@api_bp.route('/folder_info/<path:folder_path>')
def api_folder_info(folder_path):
    fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
    full_path = os.path.join(fs_model.root_dir, folder_path)

    if not os.path.abspath(full_path).startswith(os.path.abspath(fs_model.root_dir)):
        return jsonify({"error": "Acesso negado"}), 403
    
    if os.path.isdir(full_path):
        size_formatted = fs_model.get_folder_size(full_path)
        if "N/A" in size_formatted:
            return jsonify({"size": "N/A"}), 500
        return jsonify({"size": size_formatted})
    
    return jsonify({"error": "Não é uma pasta"}), 400

@api_bp.route('/search')
def search():
    query = request.args.get('q', '')
    fs_model = FileSystemModel(current_app.config['ROOT_DIR'])
    results = fs_model.search(query)
    return jsonify(results)