import click
import json
from .utils import get_config, update_config, mkdir_if_not_exists, rmdir_if_exists, write_string_to_file, get_pyproject_toml, update_pyproject_toml, get_vscode_settings, update_vscode_settings, get_project_directory, get_package_pyproject_toml, get_package_path
import pkgutil
import subprocess
import os


@click.group()
def cli():
    config = get_config()
    if not config:
        print(f'Not an omnirepo workspace')
        exit()


@click.command(help="Initialize workspace")
@click.option('--name', '-n', help='workspace name')
@click.option('--author', '-a', help='author name')
def init(name, author):
    """
    Initialize the omnirepo workspace
    :param name:
    :return:

    - create omnirepo-config.json
    - add tasks to pyproject.toml (test, lint, format, check)
    """
    click.echo(f'Creating workspace...')

    # check if already a workspace
    existing_config = get_config()
    if existing_config:
        print('Directory is already an omnirepo workspace\n\n')
        return

    # get missing args
    name = input('Enter workspace name: ') if name is None else name

    # default config
    config = {
        'workspace': name,
        'author': author if author is not None else '',
        'packages': {},
    }

    # add tasks to pyproject.toml + mypy/black config
    pyproject = get_pyproject_toml()
    if 'dependencies' not in pyproject['tool']['poetry']:
        pyproject['tool']['poetry']['dependencies'] = {}
    pyproject['tool']['poetry']['dependencies']['taskipy'] = '^1.12.2'
    pyproject['tool']['poetry']['dependencies']['pytest'] = '^8.2.0'
    pyproject['tool']['poetry']['dependencies']['mypy'] = '^1.10.0'
    pyproject['tool']['poetry']['dependencies']['flake8'] = '^7.0.0'
    pyproject['tool']['poetry']['dependencies']['black'] = '^24.4.2'

    pyproject['tool']['taskipy'] = {
        'tasks': {
            'test': 'poetry run pytest',
            'lint': 'poetry run flake8',
            'format': 'poetry run black .',
            'check': 'poetry run mypy .'
        }
    }
    pyproject['tool']['black'] = {
        'line-length': 100
    }
    pyproject['tool']['mypy'] = {
        "show_error_context": True,
        "show_column_numbers": True,
        "ignore_missing_imports": True,
        "disallow_untyped_defs": True,
        "no_implicit_optional": True,
        "warn_return_any": True,
        "warn_unused_ignore": True,
        "warn_redundant_casts": True
    }

    # update vscode settings for project
    settings = get_vscode_settings()
    settings = {} if settings is None else settings
    settings["python.formatting.provider"] = "black"
    settings["python.formatting.blackArgs"] = ["--line-length", "102"]
    settings["python.linting.flake8Enabled"] = True
    settings["python.linting.mypyEnabled"] = True
    settings["python.sortImports.args"] = ["--profile=black", "--line-length=102"]
    settings["editor.codeActionsOnSave"] = {
        "source.organizeImports": True,
        "source.fixAll": True
    }

    # Serializing json
    json_object = json.dumps(config, indent=2)

    # Writing to omnirepo.json
    with open('omnirepo-config.json', 'w') as outfile:
        outfile.write(json_object)

    click.echo("...DONE\n\n")


@click.command()
@click.argument('directory', default="package")
@click.option('--buildable', default=False, is_flag=True, help="whether package is buildable")
@click.option('--name', help='package name')
def create(directory, buildable, name):
    """
    Create a new package in the specified subdirectory
    :param directory:
    :param buildable:
    :param name:
    :return:

    - create subdirectory
    - create dir with workspace name
    - create dir with project name
    - add files based on templates (__init__, main, pyproject.toml, Makefile)
    - add package import for toplevel pyproject.toml
    """
    click.echo(f'Adding {"buildable" if buildable else ""} package...')

    # get missing args
    directory = input('Parent directory for package (default is \'./packages\'): ') if directory is None else directory
    name = input('Enter package name name: ') if name is None else name

    # read config
    config = get_config()
    if config is None:
        print('Not an omnirepo workspace')
        return

    # create folder structure
    pkg_path = f'{directory}s/{config["workspace"]}/{name}'
    mkdir_if_not_exists(pkg_path)

    # update config with project path
    projects = config['packages']
    if f'{directory}s' in projects and name in projects[f'{directory}s']:
        click.echo('Project already exists')
        return
    else:
        projects[f'{directory}s'] = [] if f'{directory}s' not in projects else projects[f'{directory}s']
        projects[f'{directory}s'].append(name)
        update_config(config)

    # update pyproject.toml
    pyproject = get_pyproject_toml()
    if 'packages' not in pyproject['tool']['poetry']:
        pyproject['tool']['poetry']['packages'] = []
    if buildable:
        pyproject['tool']['poetry']['packages'].append({
            'include': f'{name}',
            'from': f'{directory}s/{config["workspace"]}/{name}'
        })
    else:
        pyproject['tool']['poetry']['packages'].append({
            'include': f'{config["workspace"]}/{name}',
            'from': f'{directory}s'
        })
    update_pyproject_toml(pyproject)

    # get templates, use path.join?
    # print(pkgutil.get_data(__name__, f'templates/default/__init__.py.template'))
    templates_file = pkgutil.get_data(__name__, f'templates/{"buildable" if buildable else "default"}/templates.txt').decode('UTF-8')
    templates = templates_file.split('\n')
    template_strings = list(
        map(lambda t: pkgutil.get_data(__name__, f'templates/{"buildable" if buildable else "default"}/{t}.template').decode('UTF-8'), templates))
    for i in range(len(template_strings)):
        populated = (template_strings[i]
                        .replace('%WORKSPACE_NAME%', config['workspace'])
                        .replace('%PACKAGE_NAME%', name))
        path_from_proj = (templates[i]
                          .replace('%WORKSPACE_NAME%', config['workspace'])
                          .replace('%PACKAGE_NAME%', name))
        path_from_workspace_root = f'{pkg_path}/{path_from_proj}'
        write_string_to_file(populated, path_from_workspace_root)

    click.echo('...DONE')
    click.echo('Running poetry install...')
    subprocess.run(["poetry", "install"], shell=True, text=True, capture_output= True)


@click.command()
@click.argument('directory', default="package")
@click.option('--name', help='package name')
def remove(directory, name):
    """
    Remove package from workspace
    :return:
    """
    click.echo('Removing package from workspace...')
    # find project path
    config = get_config()
    if f'{directory}s' not in config['packages']:
        click.echo('Package not found')

    # remove from config
    name in config['packages'][f'{directory}s'] and config['packages'][f'{directory}s'].remove(name)
    update_config(config)

    # remove from pyproject.toml
    pyproject = get_pyproject_toml()
    if 'packages' in pyproject['tool']['poetry']:
        packages = pyproject['tool']['poetry']['packages']
        to_remove_idx = next(i for i, p in enumerate(packages) if p['include'] == f'{config["workspace"]}/{name}' or p['include'] == f'{name}')
        try:
            del pyproject['tool']['poetry']['packages'][to_remove_idx]
        except Exception as e:
            click.echo('...Package was not found in pyproject.toml')
    update_pyproject_toml(pyproject)

    # remove dir
    rmdir_if_exists(f'{directory}s/{config["workspace"]}/{name}')
    click.echo('...DONE')


@click.command()
@click.argument('command')
def run(command):
    """
    Run package "run" task if package name is provided, or task given "package:task". Otherwise, attempts to run task with given name in top-level pyproject.toml
    """
    click.echo(f'Running {command}...')
    config = get_config()
    if ':' in command:
        split = command.split(':')
        project, cmd = split[0], split[1]
        dir = get_project_directory(project)
        if dir == None:
            click.echo(f'No project found with name "{project}"')
        else:
            subprocess.run(f'cd {dir}/{config['workspace']}/{project}; poetry install; poetry run task {command}', shell=True, text=True, capture_output= False)
        # subprocess.run(f'cd poetry run task {command}', shell=True, text=True, capture_output= False)
    else:
        dir = get_project_directory(command)
        if dir == None:
            click.echo(f'No project found with name "{command}". Running top-level task...')
            subprocess.run(f'poetry run task {command}', shell=True, text=True, capture_output= False)
        else:
            try:
                pyproject = get_package_pyproject_toml(command)
                main_path = pyproject['tool']['omnirepo']['main-path']
                run_command = pyproject['tool']['omnirepo']['run-command']
                run_command = run_command.replace('%MAIN_PATH%', os.path.join(*get_package_path(command), *main_path))
                subprocess.run(run_command, shell=True, text=True, capture_output= False)
            except Exception:
                subprocess.run(f'poetry run python {dir}/{config['workspace']}/{command}/{command}', shell=True, text=True, capture_output= False)


@click.command('import')
def import_package():
    click.echo('Setting up import...')


cli.add_command(init)
cli.add_command(create)
cli.add_command(remove)
cli.add_command(run)
