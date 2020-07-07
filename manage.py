#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
import multiprocessing
from game.redis_sync import do_sync_user, do_sync_bet

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_django.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    if '--redis' in sys.argv:
        redis_index = sys.argv.index('--redis')
        sys.argv.pop(redis_index)
        redis_service = multiprocessing.Process(target=do_sync_user)
        redis_service2 = multiprocessing.Process(target=do_sync_bet)
        redis_service.start()
        redis_service2.start()

    if '--fork' in sys.argv:
        fork_index = sys.argv.index('--fork')
        if fork_index + 2 == len(sys.argv):
            sys.argv.pop(fork_index)
            pid_file = sys.argv.pop(fork_index)
            pid = os.fork()
            if pid == 0:
                # with open(pid_file, 'a') as f:
                #     f.write(str(os.getpid()) + ' ')
                main()
        else:
            print('No pid file specified. Please specify the pid file and try again')
    else:
        main()

# /var/debian-10_Buster/