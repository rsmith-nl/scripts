#!/usr/bin/env python

'Script to format a Git log for LaTeX'

import subprocess
import sys
import os

def header():
    rv = '% -*- latex -*-\n'
    rv += '% Automatisch gegenereerd door tools/mkhistory.py\n\n'
    rv += '\chapter{Wijzigingen}\n\n'
    rv += 'Dit hoofdstuk wordt automatisch gegenereerd uit het '
    rv += '\\texttt{git} revisiecontrolesysteem.\\\\\n'
    rv += 'De meest recente wijzigingen staan bovenaan.\n\n'
    return rv

def genrecords(lol):
    rv = ''
    for ln in lol:
        if ln.startswith('commit'):
            if rv:
                rv += '\end{tabular}\n\n'
                yield rv
            rv = '\\begin{tabular}{p{0.07\\textwidth}p{0.87\\textwidth}}\n'
            words = ln.split(' ', 1)
            ln = ln.replace(' ', ' & ', 1)
            rv += '  ' + words[0] + ' & ' + '\\texttt{' 
            rv += words[1] + '}\\\\\n'
        elif ln.startswith('Merge:'):
            words = ln.split(':', 1)
            rv += '  ' + words[0] + ': & ' + '\\texttt{' 
            rv += words[1].lstrip(None) + '}\\\\\n'
        elif (ln.startswith('Author:') or 
              ln.startswith('Date:')) :
            ln = ln.replace(': ', ': & ')
            rv += '  ' + ln + '\\\\\n'
        else:
            ln = ln.lstrip(None)
            if len(ln):
                rv += '  & '+ ln + '\\\\\n'
    if rv:
        rv += '\end{tabular}\n\n% EOF\n'
        yield rv
    return

if __name__ == '__main__':
    if len(sys.argv) < 2:
        path, binary = os.path.split(sys.argv[0])
        print "Gebruik: {} bestandsnaam".format(binary)
        exit(0)
    fn = sys.argv[1]
    try:
        lines = subprocess.check_output(['git', 'log']).split('\n')
    except  CalledProcessError:
        print "Git niet gevonden! Stop."
        exit(1)
    if fn == '-':
        of = sys.stdout
    else:
        of = open(fn, 'w+')
    of.write(header())
    for rec in genrecords(lines):
        of.write(rec)
    of.close()
