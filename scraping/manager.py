from datetime import datetime
from subprocess import Popen
import yaml


def run():
    config = load_config()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    indexes = split_indexes(config['leagues'], config['worker_processes'])
    print(indexes)
    for i, index in enumerate(indexes):
        Popen(f"python worker.py {i + 1} {index} {timestamp}", shell=True)
    print('Finished')


def load_config():
    with open("config.yaml", "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def split_indexes(ls, n):
    k, m = divmod(len(ls), n)
    splitted_data = list((ls[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in list(range(n))))
    count = 0
    indexes = []
    for split in splitted_data:
        indexes.append(str(count) + '-' + str(len(split) + count - 1))
        count += len(split)

    return indexes


if __name__ == '__main__':
    run()
