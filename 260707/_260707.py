import argparse

def test():
    print('hi')

if __name__ == '__main__':
    test()
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    args = parser.parse_args()

    print(args.name)