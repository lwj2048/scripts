import os

# 要检查的关键字列表
KEYWORDS = ['wwwsssxxx', 'other_keyword']

def check_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            for keyword in KEYWORDS:
                if keyword in line:
                    print(f'Error: {keyword} found in {filename}, line {i+1}')

def check_dir(dirname):
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            if filename.endswith('.py'):
                check_file(os.path.join(root, filename))

if __name__ == '__main__':
    check_dir('.')
