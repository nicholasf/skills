from .bash import bash
from .find_files import find_files
from .grep import grep
from .read_file import read_file
from .write_file import write_file

TOOLS = [read_file, bash, find_files, grep, write_file]
TOOL_MAP = {t.name: t for t in TOOLS}
