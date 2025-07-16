import os
import json
import zipfile
from datetime import datetime
from io import BytesIO
from flask import current_app
from models import Material, Product, Sale, Expense, Worker, Customer, Bank, Cheque, db
from utils import to_jalali
import logging

logger = logging.getLogger(__name__)

BACKUP_DIR = "backups"

def ensure_backup_directory():
    """Create backup directory if it doesn't exist"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def serialize_model_data(model_class):
    """Convert model data to JSON-serializable format"""
    data = []
    try:
        records = model_class.query.all()
        for record in records:
            record_dict = {}
            for column in model_class.__table__.columns:
                value = getattr(record, column.name)
                if hasattr(value, 'isoformat'):  # Handle date/datetime objects
                    value = value.isoformat()
                elif isinstance(value, float):
                    value = float(value)  # Ensure proper float serialization
                record_dict[column.name] = value
            data.append(record_dict)
        return data
    except Exception as e:
        logger.error(f"Error serializing {model_class.__name__}: {str(e)}")
        return []

def create_backup(backup_name=None):
    """Create a complete backup of all data"""
    try:
        ensure_backup_directory()
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        # Collect data from all models
        backup_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'description': 'نسخه پشتیبان سیستم حسابداری جعبه‌سازی'
            },
            'materials': serialize_model_data(Material),
            'products': serialize_model_data(Product),
            'sales': serialize_model_data(Sale),
            'expenses': serialize_model_data(Expense),
            'workers': serialize_model_data(Worker)
        }
        
        # Create backup file
        backup_filename = f"{backup_name}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add JSON data
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=2)
            zipf.writestr(f"{backup_name}.json", json_data.encode('utf-8'))
            
            # Add metadata file
            metadata = {
                'name': backup_name,
                'created_at': backup_data['metadata']['created_at'],
                'tables': {
                    'materials': len(backup_data['materials']),
                    'products': len(backup_data['products']),
                    'sales': len(backup_data['sales']),
                    'expenses': len(backup_data['expenses']),
                    'workers': len(backup_data['workers'])
                }
            }
            zipf.writestr('metadata.json', json.dumps(metadata, ensure_ascii=False, indent=2).encode('utf-8'))
        
        logger.info(f"Backup created successfully: {backup_filename}")
        return {
            'success': True,
            'filename': backup_filename,
            'path': backup_path,
            'metadata': metadata
        }
        
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def list_backups():
    """List all available backups"""
    try:
        ensure_backup_directory()
        backups = []
        
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.zip'):
                filepath = os.path.join(BACKUP_DIR, filename)
                try:
                    with zipfile.ZipFile(filepath, 'r') as zipf:
                        metadata_content = zipf.read('metadata.json').decode('utf-8')
                        metadata = json.loads(metadata_content)
                        
                        # Add file size
                        metadata['file_size'] = os.path.getsize(filepath)
                        metadata['filename'] = filename
                        
                        backups.append(metadata)
                except Exception as e:
                    logger.warning(f"Could not read metadata from {filename}: {str(e)}")
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
        
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        return []

def restore_backup(backup_filename):
    """Restore data from a backup file"""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'فایل پشتیبان یافت نشد'}
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            # Find the JSON data file
            json_filename = None
            for file_info in zipf.filelist:
                if file_info.filename.endswith('.json') and file_info.filename != 'metadata.json':
                    json_filename = file_info.filename
                    break
            
            if not json_filename:
                return {'success': False, 'error': 'فایل داده در پشتیبان یافت نشد'}
            
            # Load backup data
            json_content = zipf.read(json_filename).decode('utf-8')
            backup_data = json.loads(json_content)
        
        # Clear existing data (BE CAREFUL!)
        try:
            db.session.query(Worker).delete()
            db.session.query(Expense).delete()
            db.session.query(Sale).delete()
            db.session.query(Product).delete()
            db.session.query(Material).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'خطا در پاک کردن داده‌های قبلی: {str(e)}'}
        
        # Restore data
        restore_counts = {}
        
        # Restore materials
        if 'materials' in backup_data:
            for item_data in backup_data['materials']:
                material = Material()
                for key, value in item_data.items():
                    if key != 'id':  # Skip ID to let database auto-assign
                        if key == 'date' and isinstance(value, str):
                            value = datetime.fromisoformat(value).date()
                        setattr(material, key, value)
                db.session.add(material)
            restore_counts['materials'] = len(backup_data['materials'])
        
        # Restore products
        if 'products' in backup_data:
            for item_data in backup_data['products']:
                product = Product()
                for key, value in item_data.items():
                    if key != 'id':
                        if key == 'date' and isinstance(value, str):
                            value = datetime.fromisoformat(value).date()
                        setattr(product, key, value)
                db.session.add(product)
            restore_counts['products'] = len(backup_data['products'])
        
        # Restore sales
        if 'sales' in backup_data:
            for item_data in backup_data['sales']:
                sale = Sale()
                for key, value in item_data.items():
                    if key != 'id':
                        if key == 'date' and isinstance(value, str):
                            value = datetime.fromisoformat(value).date()
                        setattr(sale, key, value)
                db.session.add(sale)
            restore_counts['sales'] = len(backup_data['sales'])
        
        # Restore expenses
        if 'expenses' in backup_data:
            for item_data in backup_data['expenses']:
                expense = Expense()
                for key, value in item_data.items():
                    if key != 'id':
                        if key == 'date' and isinstance(value, str):
                            value = datetime.fromisoformat(value).date()
                        setattr(expense, key, value)
                db.session.add(expense)
            restore_counts['expenses'] = len(backup_data['expenses'])
        
        # Restore workers
        if 'workers' in backup_data:
            for item_data in backup_data['workers']:
                worker = Worker()
                for key, value in item_data.items():
                    if key != 'id':
                        if key == 'date' and isinstance(value, str):
                            value = datetime.fromisoformat(value).date()
                        setattr(worker, key, value)
                db.session.add(worker)
            restore_counts['workers'] = len(backup_data['workers'])
        
        db.session.commit()
        
        logger.info(f"Backup restored successfully: {backup_filename}")
        return {
            'success': True,
            'restored_counts': restore_counts,
            'backup_date': backup_data.get('metadata', {}).get('created_at')
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error restoring backup: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def delete_backup(backup_filename):
    """Delete a backup file"""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'فایل پشتیبان یافت نشد'}
        
        os.remove(backup_path)
        logger.info(f"Backup deleted: {backup_filename}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Error deleting backup: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_backup_info(backup_filename):
    """Get detailed information about a backup"""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            return None
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            metadata_content = zipf.read('metadata.json').decode('utf-8')
            metadata = json.loads(metadata_content)
            
            # Add additional info
            metadata['file_size'] = os.path.getsize(backup_path)
            metadata['filename'] = backup_filename
            
            return metadata
            
    except Exception as e:
        logger.error(f"Error getting backup info: {str(e)}")
        return None

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"