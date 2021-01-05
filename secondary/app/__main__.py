import argparse

from .app import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="secondary node")
    parser.add_argument('--host')
    parser.add_argument('--port')
    parser.add_argument('--delay', default=0, type=int)
    parser.add_argument('--error_prob', default=0, type=float)

    args = parser.parse_args()

    main(args)
