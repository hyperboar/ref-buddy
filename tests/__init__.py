import os

os.environ['APP_ENV'] = 'test'

def config_tmp_factory(source:str, new_source:str, marker:str) -> str:
    with open(source, 'r') as f:
        with open(new_source, 'w') as new_f:
            lines = []
            while line := f.readline():
                lines.append(line.replace('__', marker))
            new_f.writelines(lines)
    return new_source