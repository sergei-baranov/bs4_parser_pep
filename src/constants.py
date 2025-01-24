from pathlib import Path


MAIN_DOC_URL: str = 'https://docs.python.org/3/'
BASE_DIR: Path = Path(__file__).parent
DATETIME_FORMAT: str = '%Y-%m-%d_%H-%M-%S'

MAIN_PEP_URL: str = 'https://peps.python.org/'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
