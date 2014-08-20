#!/usr/bin/python
import os
import sys
import sqlite3
import argparse
import resource
import traceback
import subprocess

supported_langs = ['python', 'c++']

# connect to database of correct answers and timed results
db = sqlite3.connect('solutions.db')
cursor = db.cursor()

def parse_args(args):
    # parses an integer or an integer range
    def integer_list(arg):
        try:
            if '-' in arg:
                start, end = [int(a.strip()) for a in arg.split('-')]
                return range(start, end+1)
            else:
                return int(arg)
        except Exception as error:
            raise Exception('%s is not a valid integer or list' % arg)

    argp = argparse.ArgumentParser()
    argp.add_argument(
        'problems',
        type=integer_list, nargs='+',
        help='Problems to run')
    args = argp.parse_args()

    # flatten, remove duplicates, and sort problem numbers
    args.problems = [n for l in args.problems if isinstance(l, list) for n in l] + [n for n in args.problems if isinstance(n, int)]
    args.problems = sorted(set(args.problems))
    return args

def execute(query, error_message='Error: %s'):
    try:
        with db:
            db.execute(query)
    except Exception as error:
        print error_message % error

def run_solution(command, problem, language):
    lang = 'cpp' if language == 'c++' else language
    s_ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    output = subprocess.check_output(command).strip()
    e_ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    time = float(e_ru.ru_utime + e_ru.ru_stime - s_ru.ru_utime - s_ru.ru_stime)*100.0
    print '\nProblem %s %s Solution:' % (problem, language)
    print '-'*19 + ('-'*len(str(problem) + language))
    print '%s\n%sms exectution time' % (output, time) 
    cursor.execute('select * from solutions where id = %s' % problem)
    row = cursor.fetchone()
    if row:
        # check answer
        if output == row[2]:
            # insert into language table
            cursor.execute('select * from %s where id = %s' % (lang, problem))
            lang_row = cursor.fetchone()
            if not lang_row:
                execute("insert into %s values ('%s', '%s')" % (lang, problem, time),
                        ('Error inserting %s into db: ' % problem) + '%s')               
            # check time
            fastest = float(row[3])
            if time < fastest:
                # update db, new fastest time
                print 'New fastest time!'
                execute("update solutions set language = '%s', speed = '%s' where id = %s" % (language, time, problem),
                        ('Error updating problem %s: ' % problem) + '%s')
                
                execute("update %s set speed = '%s' where id = %s" % (lang, time, problem),
                        ('Error updating problem %s: ' % problem) + '%s')
        else:
            print 'Incorrect answer %s for problem %s: correct answer is %s' % (output, problem, row[2])
    else:
        # insert into db if correct
        confirmation = raw_input("Correct solution to problem %s? (Enter 'y' to update db):" % problem)
        if confirmation.strip() == 'y':
            execute("insert into solutions values (%s, '%s', '%s', '%s')" % (problem, language, output, time),
                    ('Error inserting %s into db: ' % problem) + '%s')
            execute("insert into %s values ('%s', '%s')" % (lang, problem, time),
                    ('Error inserting %s into db: ' % problem) + '%s')

def main(args):
    args = parse_args(args)
    # iterate over given problems and found languages
    for problem in args.problems:
        languages = [dir for dir in os.listdir(os.getcwd()) if os.path.isdir(dir) and dir in supported_langs]
        for language in languages:
            if language == 'python':
                file = os.path.join(os.getcwd(), language, str(problem), 'problem_%s.py' % problem)
                # execute python files and print output
                if os.path.exists(file) and os.path.isfile(file):
                    run_solution(['python', file], problem, language)
            elif language == 'c++':
                # compile and run c++
                file = os.path.join(os.getcwd(), language, str(problem), 'problem_%s.cpp' % problem)
                if os.path.exists(file) and os.path.isfile(file):
                    exe = os.path.join(os.getcwd(), language, str(problem), 'problem_%s' % problem)
                    output = subprocess.check_output(['g++', file, '-o', exe, '-O3', '-I', os.path.join(os.getcwd(), 'pe_cpp_utils')])
                    if output.strip():
                        raise Exception('Error: %s failed to compile: %s' % (exe, output.strip()))
                    run_solution([exe], problem, language)
                    # cleanup: delete executable
                    os.remove(exe)
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

