import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import traceback
import inspect
from functools import wraps

from configs import constant

# Đường dẫn thư mục gốc để lưu log
LOG_PATH = constant.LOG_PATH


# Hàm tạo thư mục log nếu chưa tồn tại
def create_log_directories():
    """
    Tạo thư mục log theo năm và tháng nếu chưa tồn tại.
    Trả về đường dẫn của thư mục log hiện tại.
    """
    try:
        # Lấy thời gian hiện tại để tạo thư mục theo năm và tháng
        current_time = datetime.now()
        year_dir = os.path.normpath(os.path.join(LOG_PATH, str(current_time.year)))
        month_dir = os.path.normpath(os.path.join(year_dir, f"{current_time.month:02d}"))

        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(month_dir, exist_ok=True)
        return month_dir
    except Exception as e:
        print(f"Lỗi khi tạo thư mục log: {e}")
        raise


# Hàm cấu hình logger theo mức độ và đường dẫn file log
def get_logger(logger_name, log_file, level=logging.INFO):
    """
    Tạo hoặc lấy logger với tên và mức độ đã cho.
    """
    logger = logging.getLogger(logger_name)

    # Nếu logger chưa có handler thì thêm mới
    if not logger.hasHandlers():
        try:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

            # Sử dụng TimedRotatingFileHandler để tạo log xoay vòng theo ngày
            file_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
            file_handler.suffix = "%Y-%m-%d"
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)

            logger.addHandler(file_handler)
            logger.setLevel(level)
        except Exception as e:
            print(f"Lỗi khi tạo logger: {e}")
            raise
    return logger


# Hàm ghi log duy nhất
def write_log(level, message):
    """
    Ghi log theo mức độ và thông điệp.
    Args:
        level (str): Mức độ log ('info', 'error', 'critical')
        message (str): Thông điệp cần ghi vào log
    """
    try:
        # Bước 1: Tạo thư mục log hiện tại theo năm và tháng
        log_directory = create_log_directories()

        # Bước 2: Đường dẫn file log theo ngày hiện tại
        daily_log_file = os.path.normpath(os.path.join(log_directory, f"{datetime.now().day:02d}.log"))

        # Bước 3: Tạo logger tương ứng theo mức độ
        if level == 'info':
            logger = get_logger('info_logger', daily_log_file, logging.INFO)
        elif level == 'error':
            logger = get_logger('error_logger', os.path.join(log_directory, 'errors.log'), logging.ERROR)
        elif level == 'critical':
            logger = get_logger('critical_logger', os.path.join(LOG_PATH, 'critical_errors.log'), logging.CRITICAL)
        else:
            # Mặc định nếu không đúng level, ghi vào info log
            logger = get_logger('info_logger', daily_log_file, logging.INFO)
            logger.warning(f"Unknown log level: {level}. Message: {message}")
            return

        # Bước 4: Ghi log
        # logger.log(getattr(logging, level.upper()), message)
    except Exception as e:
        print(f"Lỗi trong quá trình ghi log: {e}")
        raise

    try:
        # Bước 1: Tạo thư mục log hiện tại theo năm và tháng
        log_directory = create_log_directories()

        # Bước 2: Đường dẫn file log theo ngày hiện tại với đuôi .txt
        daily_log_file = os.path.normpath(os.path.join(log_directory, f"{datetime.now().day:02d}.txt"))

        # Bước 3: Tạo logger tương ứng theo mức độ
        if level == 'info':
            logger = get_logger('info_logger', daily_log_file, logging.INFO)
        elif level == 'error':
            logger = get_logger('error_logger', os.path.join(log_directory, 'errors.txt'), logging.ERROR)
        elif level == 'critical':
            logger = get_logger('critical_logger', os.path.join(LOG_PATH, 'critical_errors.txt'), logging.CRITICAL)
        else:
            # Mặc định nếu không đúng level, ghi vào info log
            logger = get_logger('info_logger', daily_log_file, logging.INFO)
            logger.warning(f"Unknown log level: {level}. Message: {message}")
            return

        # Bước 4: Ghi log
        # logger.log(getattr(logging, level.upper()), message)
    except Exception as e:
        print(f"Lỗi trong quá trình ghi log: {e}")
        raise


# Decorator để log tên hàm và tự động log exception
def log_function(func):
    """
    Decorator để tự động ghi log khi hàm được gọi và log lỗi nếu có exception.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        arguments = inspect.signature(func).bind(*args, **kwargs)
        arguments.apply_defaults()
        args_str = ', '.join([f"{k}={v!r}" for k, v in arguments.arguments.items()])
        write_log('info', f"Calling function: {func_name}({args_str})")

        try:
            result = func(*args, **kwargs)
            write_log('info', f"Function {func_name} completed successfully.")
            return result
        except Exception as e:
            error_message = f"Exception in function {func_name}: {str(e)}\n{traceback.format_exc()}"
            write_log('error', error_message)
            raise e

    return wrapper
