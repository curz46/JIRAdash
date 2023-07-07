import os

# Program name
PROGRAM_NAME = "JIRAdash"

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIRS = [
    "/usr/local/etc/" + PROGRAM_NAME,
    os.path.expanduser("~/.config/" + PROGRAM_NAME),
    os.path.join(SCRIPT_DIR, PROGRAM_NAME),
]

# Files to find
FILES = ["styles.css", "issues.db", "schema.json"]

STYLES_DEFAULT = """
* {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
}

window {
    background-color: #F0F0F0;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

entry {
    min-height: 30px;
    padding: 5px 10px;
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 3px;
}

entry:focus {
    border-color: #66AFE9;
}

listbox {
    background-color: #FFFFFF;
}

label {
    padding: 5px 10px;
    color: #333333;
}

label:hover {
    background-color: #F0F0F0;
}

box {
    padding: 10px;
}"""

def get_paths():

    # Create a dictionary to store the file paths
    file_paths = {}

    # Loop through the directories and look for the files
    for config_dir in CONFIG_DIRS:
        for file_name in FILES:
            file_path = os.path.join(config_dir, file_name)
            if os.path.exists(file_path):
                file_paths[file_name] = file_path
                break

    # Create default directories and files
    for file_name in FILES:
        if file_name not in file_paths:
            file_dir = os.path.join(os.path.expanduser("~/.config"), PROGRAM_NAME)
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, file_name)
            file_paths[file_name] = file_path

    if not os.path.exists(file_paths["styles.css"]):
        with open(file_paths["styles.css"], "w") as f:
            f.write(STYLES_DEFAULT)

    return file_paths
