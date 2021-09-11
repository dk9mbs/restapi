from core.log import create_logger

logger=create_logger(__name__)

class FileSystemTools:
    @staticmethod
    def format_path(path):
        if path.endswith("/"):
            return path
        else:
            return f"{path}/"
