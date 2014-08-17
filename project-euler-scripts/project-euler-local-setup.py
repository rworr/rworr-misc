#!/usr/bin/python
import os
import sys
import urllib2
import sqlite3
import traceback
from string import Template
from argparse import ArgumentParser

python_file_format =  Template("""# Project Euler Problem $problem
$description

import sys
import traceback

def main():
    print "TODO"

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except (ValueError, IOError) as error:
        print '%s: %s' % (type(error).__name__, error)
    except Exception as error:
        print 'Uncaught Error: %s\\n%s' % (type(error).__name__, traceback.format_exc())

""")

cpp_file_format = Template("""// Project Euler Problem $problem
$description

#include <iostream>

using namespace std;

int main() {
    cout << "TODO" << endl;
    return 0;
}
""")

def parse_args(args):
    # Checks if the directory is valid
    def valid_dir(path):
        if not os.path.exists(path):
            raise Exception('Unable to setup: directory %s does not exist' % path)
        if not os.path.isdir(path):
            raise Exception('Unable to setup: %s is not a directory' % path)
        return path
    
    # Checks if the given list of languages is supported
    def language_list(list):
        supported_languages = ['python', 'c++']
        langs = [l.strip() for l in list.split(',')]
        for lang in langs:
            if lang not in supported_languages:
                raise Exception('Unable to setup: %s is not a supported language')
        return langs

    argp = ArgumentParser(description='Project Euler local setup')
    argp.add_argument(
        '--start-problem', metavar='S',
        type=int, default=1,
        help='First problem to pull')
    argp.add_argument(
        '--num-problems', metavar='N',
        type=int, default=10,
        help='Number of problems to pull')
    argp.add_argument(
        '--languages', metavar='L1,L2,...',
        default='python', type=language_list,
        help='comma-separated list of languages to setup')
    argp.add_argument(
        '--root-directory', metavar='PATH',
        type=valid_dir, default=os.getcwd(),
        help='root directory for setup')
    args = argp.parse_args()
    return args

def execute(query, error_message='Error: %s'):
    try:
        with db:
            db.execute(query)
    except Exception as error:
        print error_message % error

# Returns false if the directory did not exist previously
def dir_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)
        return False
    elif not os.path.isdir(path):
        raise Exception('Unable to setup: %s already exists and is not a directory' % lang_dir)
    return True

# Removes any html tags
def strip_html_tags(html):
    while '<' in html:
        tag_start_idx = html.index('<')
        tag_end_idx = html.index('>', tag_start_idx) + 1
        if 'td' in html[tag_start_idx:tag_end_idx]:
            html = html[:tag_start_idx] + ' ' + html[tag_end_idx:]
        else:
            html = html[:tag_start_idx] + html[tag_end_idx:]
    return html

# Removes any html comments
def strip_html_comments(html):
    while '<!--' in html:
        comment_start_idx = html.index('<!--')
        comment_end_idx = html.index('-->', comment_start_idx) + len('-->') + 1
        html = html[:comment_start_idx] + html[comment_end_idx:]
    return html

# Returns a list of links to data files
def parse_data_files(html):
    links = []
    while 'a href=' in html:
        cur_idx = html.index('a href')
        link_start_single = html.find("'", cur_idx)
        link_start_double = html.find('"', cur_idx)
        if (link_start_double == -1 or link_start_single < link_start_double) and link_start_single != -1:
            link_start = link_start_single + 1 
            link_end = html.index("'", link_start)
        elif (link_start_single == -1 or link_start_double < link_start_single) and link_start_double != -1:
            link_start = link_start_double + 1
            link_end = html.index('"', link_start)
        link = 'http://projecteuler.net/' + html[link_start:link_end]
        data = urllib2.urlopen(link).read()
        if not ('<html' in data and '<head>' in data and '<body>' in data):
            links.append(link) 
        html = html[link_end:]
    return links

def main(args):
    args = parse_args(args)

    # check for language directories
    for lang in args.languages:
        dir_exists(os.path.join(args.root_directory, lang))
        
    # check for doc directories
    doc_dir = os.path.join(args.root_directory, 'doc')
    dir_exists(doc_dir)

    # pull projects
    for problem in range(args.start_problem, args.start_problem + args.num_problems):
        # parse problem description from projecteuler.net
        problem_html = urllib2.urlopen('http://projecteuler.net/problem=%s' % problem).read()
        problem_content_start = problem_html.index('>', problem_html.index('problem_content')) + 1
        problem_content_end = 0
        cur_idx = problem_content_start
        # find the div enclosing the description
        while problem_content_end == 0:
            div_idx = problem_html.index('<div', cur_idx)
            div_end_idx = problem_html.index('</div', cur_idx)
            if div_idx < div_end_idx and div_idx != -1:
                cur_idx = div_end_idx + 1
            else:
                problem_content_end = div_end_idx
        problem_html = problem_html[problem_content_start:problem_content_end].strip()
        files = parse_data_files(problem_html)
        description = strip_html_tags(strip_html_comments(problem_html))
        description = '\n'.join(filter(None, [line.strip() for line in description.split('\n')]))

        # create directories
        for lang in args.languages:
            path = os.path.join(args.root_directory, lang, str(problem))
            if dir_exists(path):
                print '%s already exists; skipping' % path
                continue
            # write file templates
            if lang == 'python':
                with open(os.path.join(path, 'problem_%s.py' % problem), 'w') as template:
                    comments = '\n'.join(['# %s' % line for line in description.split('\n')])
                    template.write(python_file_format.substitute(problem=problem, description=comments))
            elif lang == 'c++':
                with open(os.path.join(path, 'problem_%s.cpp' % problem), 'w') as template:
                    comments = '\n'.join(['// %s' % line for line in description.split('\n')])
                    template.write(cpp_file_format.substitute(problem=problem, description=comments))
            # write data files
            for file in files:
                filename = file.split('/')[-1].split('#')[0].split('?')[0]
                with open(os.path.join(path, filename), 'w') as datafile:
                    datafile.write(urllib2.urlopen(file).read())

        # write description into doc
        path = os.path.join(doc_dir, 'problem_%s.txt' % problem)
        with open(path, 'w') as doc_file:
            doc_file.write(description)

        # create db if it doesn't exist
        db_path = os.path.join(args.root_directory, 'solutions.db')
        if not os.path.exists(db_path):
            global db
            db = sqlite3.connect(db_path)
            # create solutions table
            execute('CREATE TABLE solutions (id integer primary key, language text, solution text, speed text)',
                    'Error creating table: %s')
            db.close()

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
    except (ValueError, IOError) as error:
        print '%s: %s' % (type(error).__name__, error)
    except Exception as error:
        print 'Uncaught Error: %s:\n%s' % (type(error).__name__, traceback.format_exc())

