"""
Copyright 2022 Objectiv B.V.
"""

# templates
from termcolor import colored

GTIHUB_ISSUE_DATE_STR_FORMAT = '%Y%m%d_%H%M%S'
GITHUB_ISSUE_FILENAME_TEMPLATE = 'github_issue_{date_str}.md'
GITHUB_ISSUE_TEMPLATE = """
**[Notebook: {engine}]** {notebook} failing.
_____

Please check cell number: {cell_number}

Failing code:

```python
{failing_code}
```

Raised exception:
{exception}
"""


NB_SCRIPT_TO_STORE_TEMPLATE = """
def {notebook}():
    {script}


if __name__ == '__main__':
    {notebook}()
"""

SET_ENV_VARIABLE_TEMPLATE = 'os.environ["{env_var_name}"] = "{env_var_value}"'

# notebook check settings defaults
NOTEBOOK_EXTENSION = 'ipynb'
DEFAULT_NOTEBOOKS_DIR = f'../../../notebooks/*.{NOTEBOOK_EXTENSION}'
DEFAULT_GITHUB_ISSUES_DIR = 'github_nb_issues'


# check results
REPORT_HEADERS = ['notebook', 'engine', 'status', 'failing cell', 'elapsed_time (seconds)']
ELAPSED_TIME_CELL_HEADER = 'elapsed_time per cell (seconds)'
SUCCESS_CHECK_MESSAGE = colored('Successful checks: {success_checks} ({perc_success}%)', 'green')
SKIPPED_CHECK_MESSAGE = colored('Skipped checks: {skipped_checks} ({perc_skipped}%)', 'yellow')
FAILED_CHECK_MESSAGE = colored('Failed checks: {failed_checks} ({perc_failed}%)', 'red')
MORE_INFORMATION_MESSAGE = (
    'Dear Watson, for more information about failed checks, please see: '
    f"{colored('{github_issue_file}', 'blue')} file."
)


DATE_FORMAT = '%Y-%m-%d'
