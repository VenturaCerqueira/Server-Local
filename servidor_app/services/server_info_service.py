# servidor_app/services/server_info_service.py
import psutil

def get_server_info(root_dir):
    """
    Coleta informações de uso de memória e disco.
    """
    memory_percent = psutil.virtual_memory().percent
    total_memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    
    try:
        disk_usage = psutil.disk_usage(root_dir)
        disk_percent = disk_usage.percent
        total_disk_gb = round(disk_usage.total / (1024**3), 2)
    except FileNotFoundError:
        # Lida com o caso em que o disco/caminho não existe
        disk_percent = 0
        total_disk_gb = 0
    
    return {
        'memory_percent': memory_percent,
        'total_memory_gb': total_memory_gb,
        'disk_percent': disk_percent,
        'total_disk_gb': total_disk_gb
    }