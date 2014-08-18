#!/usr/bin/python
import os
import sys
import sqlite3
import argparse
import traceback

def parse_args(args):
    argp = argparse.ArgumentParser()
    argp.add_argument('--output-file', '-o', metavar='PATH',
            help='Output file for database dump')
    args = argp.parse_args(args)
    return args

def gen_table(table, output):
    cursor = db.cursor()
    if table == 'solutions':
        output.write('Fastest Solutions:\n')
        output.write(' Problem Number |  Language  | Time (ms) \n')
        output.write('----------------+------------+-----------\n')
        for row in cursor.execute('select * from solutions order by id'):
            problem_number, language, answer, time = [str(i) for i in row]
            output.write(' '*(15-len(problem_number)) + problem_number + ' |' + ' '*(11-len(language)) + language + ' |' + ' '*(10-len(time)) + time + '\n')
    else:
        output.write('\n%s\n' % table)
        output.write(' Problem Number | Time (ms) \n')
        output.write('----------------+-----------\n')
        for row in cursor.execute('select * from %s order by id' % table):
            problem_number, time = [str(i) for i in row]
            output.write(' '*(15-len(problem_number)) + problem_number + ' |' + ' '*(10-len(time)) + time + '\n')

def main(args):
    global db
    args = parse_args(args)
    db_path = os.path.join(os.getcwd(), 'solutions.db')
    db = sqlite3.connect(db_path)
    t_cursor = db.cursor()
    with open(args.output_file, 'w') as output:
        for row in t_cursor.execute("select name from sqlite_master where type='table'"):
            gen_table(row[0], output)
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

