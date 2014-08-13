#!/usr/bin/python
import os
import sys
import argparse
import traceback
import subprocess
import resource

supported_langs = ['python', 'c++']

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

def main(args):
    args = parse_args(args)
    prev_time = 0.0
    # iterate over given problems and found languages
    for problem in args.problems:
        languages = [dir for dir in os.listdir(os.getcwd()) if os.path.isdir(dir) and dir in supported_langs]
        for language in languages:
            if language == 'python':
                file = os.path.join(os.getcwd(), language, str(problem), 'problem_%s.py' % problem)
                # execute python files and print output
                if os.path.exists(file) and os.path.isfile(file):
                    output = subprocess.check_output(['python', file])
                    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
                    print '\nproblem_%s.py: output:' % problem
                    print '--------------------' + ('-'*len(str(problem)))
                    print '%s%sms exectution time\n' % (output, float(ru.ru_utime + ru.ru_stime - prev_time)*100.0) 
                    prev_time = ru.ru_utime + ru.ru_stime
            elif language == 'c++':
                # compile and run c++
                pass

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        pass
    except (ValueError, IOError) as error:
        print '%s: %s' % (type(error).__name__, error)
    except Exception as error:
        print 'Uncaught Error: %s:\n%s' % (type(error).__name__, traceback.format_exc())

