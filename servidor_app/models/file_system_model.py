# servidor_app/models/file_system_model.py
import os
import datetime
import zipfile
from io import BytesIO
from werkzeug.utils import secure_filename

class FileSystemModel:
    """
    Gerencia todas as operações do sistema de arquivos para a aplicação.
    """
    def __init__(self, root_dir):
        if not os.path.isdir(root_dir):
            raise FileNotFoundError(f"O diretório raiz especificado não existe: {root_dir}")
        self.root_dir = root_dir

    def _format_size(self, size_bytes):
        if size_bytes is None:
            return "N/A"
        if size_bytes >= 1024**3:
            return f"{round(size_bytes / (1024**3), 2)} GB"
        elif size_bytes >= 1024**2:
            return f"{round(size_bytes / (1024**2), 2)} MB"
        elif size_bytes >= 1024:
            return f"{round(size_bytes / 1024, 2)} KB"
        else:
            return f"{size_bytes} B"

    def get_folder_size(self, path):
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except (PermissionError, FileNotFoundError):
            return "N/A"
        return self._format_size(total_size)
    
    def list_directory(self, sub_path=''):
        full_path = os.path.join(self.root_dir, sub_path)
        
        if not os.path.abspath(full_path).startswith(os.path.abspath(self.root_dir)):
            raise PermissionError("Acesso negado.")
        
        if not os.path.exists(full_path):
            raise FileNotFoundError("Caminho não encontrado.")

        items = sorted(os.listdir(full_path))
        result_list = []
        
        for item in items:
            if item.startswith('.'):
                continue

            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            
            # AJUSTE: Coleta ambas as datas, de modificação e de criação.
            modified_at = datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%d/%m/%Y %H:%M')
            created_at = datetime.datetime.fromtimestamp(os.path.getctime(item_path)).strftime('%d/%m/%Y %H:%M')
            
            item_data = {
                'nome': item,
                'path': os.path.join(sub_path, item).replace('\\', '/'),
                'is_dir': is_dir,
                'modified_at': modified_at,
                'created_at': created_at,
            }

            if is_dir:
                try:
                    contents = [name for name in os.listdir(item_path) if not name.startswith('.')]
                    item_data['file_count'] = sum(1 for name in contents if os.path.isfile(os.path.join(item_path, name)))
                    item_data['folder_count'] = sum(1 for name in contents if os.path.isdir(os.path.join(item_path, name)))
                except (PermissionError, FileNotFoundError):
                    item_data['file_count'] = "N/A"
                    item_data['folder_count'] = "N/A"
                item_data['size'] = 'calculando...'
            else:
                size_bytes = os.path.getsize(item_path)
                item_data['size'] = self._format_size(size_bytes)
                item_data['size_bytes'] = size_bytes
                item_data['type'] = item.split('.')[-1].lower() if '.' in item else 'file'
            
            result_list.append(item_data)
        
        parent_path = os.path.dirname(sub_path).replace('\\', '/') if sub_path else None
        
        return result_list, sub_path, parent_path

    def search(self, query):
        results = []
        clean_query = query.lower()
        if not clean_query:
            return results
        try:
            for root, dirs, files in os.walk(self.root_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
                
                for name in dirs + files:
                    if clean_query in name.lower():
                        full_path = os.path.join(root, name)
                        rel_path = os.path.relpath(full_path, self.root_dir).replace('\\', '/')
                        is_dir = os.path.isdir(full_path)
                        results.append({
                            'nome': name,
                            'path': rel_path,
                            'is_dir': is_dir
                        })
        except PermissionError:
            pass
        return results

    def create_zip_from_folder(self, folder_path):
        full_path = os.path.join(self.root_dir, folder_path)
        if not os.path.isdir(full_path):
            return None, None
            
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(full_path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
                
                for file in files:
                    file_full_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_full_path, full_path)
                    zf.write(file_full_path, arcname)

        memory_file.seek(0)
        download_name = f"{os.path.basename(full_path)}.zip"
        return memory_file, download_name

    def save_file(self, file, sub_path=''):
        full_path = os.path.join(self.root_dir, sub_path)
        if not os.path.abspath(full_path).startswith(os.path.abspath(self.root_dir)):
            raise PermissionError("Acesso negado.")

        filename = secure_filename(file.filename)
        file_path = os.path.join(full_path, filename)
        file.save(file_path)
        return filename

    def create_folder(self, folder_name, sub_path=''):
        full_path = os.path.join(self.root_dir, sub_path)
        if not os.path.abspath(full_path).startswith(os.path.abspath(self.root_dir)):
            raise PermissionError("Acesso negado.")

        new_folder_path = os.path.join(full_path, secure_filename(folder_name))
        
        if os.path.exists(new_folder_path):
            raise FileExistsError(f'O caminho "{new_folder_path}" já existe.')
        
        os.makedirs(new_folder_path)