import os
import logging
import shutil

from .config import PLY_DIR, TEXTURE_DIR, BACKUP_TEXTURE_DIR

logger = logging.getLogger(__name__)


def _save_original_version(mesh_id):
    erdstall_path = os.path.join(PLY_DIR, mesh_id)
    if not os.path.exists(erdstall_path):
        raise FileNotFoundError(f"Erdstall directory not found: {mesh_id}")

    backup_path = os.path.join(erdstall_path, BACKUP_TEXTURE_DIR)
    current_path = os.path.join(erdstall_path, TEXTURE_DIR)

    if not os.path.exists(current_path):
        raise FileNotFoundError(f"Texture directory not found: {current_path}")

    if not os.path.exists(backup_path):
        try:
            os.makedirs(backup_path)
            for filename in os.listdir(current_path):
                src_path = os.path.join(current_path, filename)
                dst_path = os.path.join(backup_path, filename)
                shutil.copy2(src_path, dst_path)
        except Exception as e:
            logger.error(f"Failed to create backup textures directory: {str(e)}", exc_info=True)
            raise


def get_current_version_path(mesh_id):
    _save_original_version(mesh_id)
    return os.path.join(PLY_DIR, mesh_id, TEXTURE_DIR)


def delete_new_version(mesh_id):
    _save_original_version(mesh_id)
    current_path = get_current_version_path(mesh_id)
    backup_path = os.path.join(os.path.dirname(current_path), BACKUP_TEXTURE_DIR)

    try:
        for element in os.listdir(current_path):
            path = os.path.join(current_path, element)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        for filename in os.listdir(backup_path):
            src_path = os.path.join(backup_path, filename)
            dst_path = os.path.join(current_path, filename)
            shutil.copy2(src_path, dst_path)

    except Exception as e:
        logger.error(f"Error deleting version: {str(e)}", exc_info=True)
        raise