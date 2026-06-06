import os
import json
import datetime
import colorama

def time_extension():
    """
    Generate a timestamp string with safe characters for filenames.
    """
    return str(datetime.datetime.now()).replace("-", "_").replace(" ", "T").replace(":", "_").replace(".", "_").replace(".","Z")

def create_directory(path, method_name):
    """
    Create a directory with timestamp appended to method name.
    """
    dir_stamp = time_extension()
    directory_name = f"{path}/{method_name}_{dir_stamp}"
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return directory_name

def create_log_file(test_name):
    """
    Create a log file for the given test name.
    """
    # Ensure logs directory exists relative to project root
    project_root = os.path.dirname(os.path.dirname(__file__))
    logs_dir = os.path.join(project_root, "artifacts", "logs")
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception as e:
        print(f"Could not create logs directory '{logs_dir}': {e}")

    log_filename = os.path.join(
        logs_dir,
        f"log_{test_name}_" + f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    )
    with open(log_filename, "w+", encoding="utf-8") as f:
        f.write("Session started...")
    return log_filename

def read_credentials():
    """
    Read JSON credentials from file.
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        cred_path = os.path.join(project_root, 'data', 'crdential.json')
        with open(cred_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Credential file not found at {cred_path}!")
        return None
    except json.JSONDecodeError:
        print("Invalid JSON format!")
        return None

def debug_print(file_name, status, message):
    """
    Print debug messages with color-coded output and log to file.
    """
    colorama.init(autoreset=True)
    date_time = str(datetime.datetime.now()).split(':', maxsplit=1)[0]
    debug_message = f"{date_time} : {status} : {message}"

    if status == "INFO":
        print(colorama.Fore.RESET + f"{date_time}" + ":" +
              colorama.Fore.GREEN + f"{status}" + ":" +
              colorama.Fore.RESET + f"{message}")
    elif status == "WARNING":
        print(colorama.Fore.YELLOW + f"{debug_message}")
    elif status == "ERROR":
        print(colorama.Fore.RED + f"{debug_message}")
    else:
        print(f"{debug_message}")

    with open(file_name, "a", encoding="utf-8") as file:
        file.write(f"\n{debug_message}")
        file.close()

if __name__ == "__main__":
    F_NAME = create_log_file("E2E")
    debug_print(F_NAME, "INFO", "I am Here")
    debug_print(F_NAME, "WARNING", "This is a debug message *** ...")
    debug_print(F_NAME, "ERROR", "This is a ERROR message")
    get_data = read_credentials()
    if get_data:
        data = json.dumps(get_data.get('FORMS_DATA', {}), indent=4)
        print(data)