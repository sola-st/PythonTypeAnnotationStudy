# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
from pprint import pprint
import re
import requests
import six


NUMS_PAT = re.compile(r'^@@ -([0-9]+),?([0-9]+)? \+([0-9]+),?([0-9]+)? @@')
FIRST = {' ', '+', '-'}
EMPTY_PAT = re.compile(r'^[+-][ \t]*(?://.*)?(?:/\*[^\*]*[\*]+/)?[ \t]*$')


class Patch(object):
    """The goal of Patch is to be able to parse a patch coming
       from a stream to limit memory use.
       The parse method return a dictionary containing the
       interesting files (.cpp, .h, ...) and the modified lines.
       By the way, the 'empty' lines (whites or comments) are removed.
    """

    def __init__(self, lines_gen, file_filter=None,
                 skip_comments=True, add_lines_for_new=True):
        assert isinstance(skip_comments, bool)
        self.index = 0
        self.lines = []
        self.N = 0
        self.get_lines = self._lines(lines_gen)
        self.conditions = []
        self.added = None
        self.deleted = None
        self.results = {}
        self.filename = ''
        self.changeset = ''
        self.file_filter = file_filter
        self.skip_comments = skip_comments
        self.add_lines_for_new = add_lines_for_new

    @staticmethod
    def parse_changeset(base_url, chgset, chunk_size=1000000,
                        file_filter=None, skip_comments=True,
                        add_lines_for_new=True):

        def lines_chunk(it):
            last = None
            for chunk in it:
                chunk = chunk.split('\n')
                if last is not None:
                    chunk[0] = last + chunk[0]
                last = chunk.pop()
                yield chunk

        url = '{}/{}'.format(base_url, chgset)
        r = requests.get(url, stream=True)
        it = r.iter_content(chunk_size=chunk_size,
                            decode_unicode=True)
        p = Patch(
            lines_chunk(it),
            file_filter=file_filter,
            skip_comments=skip_comments,
            add_lines_for_new=add_lines_for_new,
        )
        p.changeset = chgset
        return p.parse()

    @staticmethod
    def parse_patch(patch, file_filter=None, skip_comments=True,
                    add_lines_for_new=True):
        if isinstance(patch, six.string_types):
            patch = patch.split('\n')

        def gen(x):
            yield x

        p = Patch(
            gen(patch),
            file_filter=file_filter,
            skip_comments=skip_comments,
            add_lines_for_new=add_lines_for_new,
        )
        return p.parse()

    @staticmethod
    def parse_file(filename, file_filter=None, skip_comments=True,
                   add_lines_for_new=True):
        with open(filename, 'r') as In:
            patch = In.read()
            return Patch.parse_patch(patch,
                                     file_filter=file_filter,
                                     skip_comments=skip_comments,
                                     add_lines_for_new=add_lines_for_new)

    def filter_file(self, f):
        if self.file_filter is not None:
            return self.file_filter(f)
        return True

    def neighbourhood(self, index):
        print('----------------------------------')
        print('INDEX = ' + str(index))
        for i in range(index - 5, index + 6):
            if i == index:
                print('~~~~~~~~~~~~~~~~~~~')
                print(self.lines[i])
                print('~~~~~~~~~~~~~~~~~~~')
            else:
                print(self.lines[i])
        print('----------------------------------')

    def _get_lines(self, lines_gen):
        for lines in lines_gen:
            self.N = len(lines)
            if self.index < self.N:
                self.lines = lines
                n = (yield)
                if n is not None:
                    self.index = n
            else:
                self.index -= self.N

    def _lines(self, lines_gen):
        gen = self._get_lines(lines_gen)
        for _ in gen:
            while self.index < self.N:
                line = self.lines[self.index]
                if self._check(line):
                    n = (yield line)
                    if n is None:
                        n = 1
                    diff = self.N - (self.index + n)
                    if diff <= 0:
                        try:
                            # no more data
                            gen.send(-diff)
                        except StopIteration:
                            # raise StopIteration
                            return
                    else:
                        self.index += n
                else:
                    if self.conditions:
                        self.conditions.pop()
                    yield None

    def _check(self, line):
        if self.conditions:
            return self.conditions[-1](line)
        return True

    def _condition(self, checker):
        self.conditions.append(checker)

    def line(self):
        return self.lines[self.index]

    def move(self, n=1):
        self.get_lines.send(n)

    def first(self):
        line = self.line()
        return line[0] if line else ''

    def parse_numbers(self, line=None):
        if not line:
            line = self.line()
        m = NUMS_PAT.search(line)
        n = [int(x) if x else 1 for x in m.groups()]
        return n[:2], n[2:]

    def skip_binary(self):
        self._condition(lambda x: bool(x))
        for line in self.get_lines:
            if line is None:
                break

    def is_binary(self):
        return self.line() == 'GIT binary patch'

    def skip_deleted_file(self):
        self.skip_useless()
        if self.is_binary():
            self.skip_binary()
        elif self.line().startswith('@'):
            minus, _ = self.parse_numbers()
            self.move(minus[1])

    def skip_new_file(self):
        plus = None
        self.skip_useless()
        if self.is_binary():
            self.skip_binary()
        elif self.line().startswith('@'):
            _, plus = self.parse_numbers()
            self.move(plus[1])
        if self.filename:
            self.results[self.filename] = {'new': True}
            if plus and self.add_lines_for_new:
                self.added = list(range(1, plus[1] + 1))
                self.deleted = []

    def next_diff(self):
        self._condition(lambda x: not x.startswith('diff --git a/') and not x.startswith('diff -r '))
        for line in self.get_lines:
            if line is None:
                return True
        return False

    def get_files(self):
        line = self.line()
        toks = line.split(' ')
        old_p = toks[2]
        old_p = old_p[2:] if old_p.startswith('a/') else old_p
        new_p = toks[3]
        new_p = new_p[2:] if new_p.startswith('b/') else new_p
        self.added = []
        self.deleted = []
        if self.filter_file(new_p):
            self.filename = new_p
            return True
        else:
            self.filename = ''
        return False

    def skip_useless(self):

        def start_filt(x):
            return x.startswith('---') or \
                x.startswith('+++') or \
                x.startswith('index ') or \
                x.startswith('old mode') or \
                x.startswith('new mode')

        self._condition(start_filt)
        for line in self.get_lines:
            if line is None:
                break

    def get_signed_count(self, line, count):
        if self.skip_comments and EMPTY_PAT.match(line):
            return -count
        return count

    def count_minus(self, count):
        self._condition(lambda x: x.startswith('-'))
        for line in self.get_lines:
            if line is None:
                break
            scount = self.get_signed_count(line, count)
            self.deleted.append(scount)
            count += 1

    def parse_hunk(self, line):

        def check(x):
            if x:
                return x[0] in FIRST
            return False

        _, plus = self.parse_numbers(line)
        count = plus[0]
        self._condition(check)
        for line in self.get_lines:
            if line is None:
                break
            first = line[0]
            if first == ' ':
                count += 1
            elif first == '+':
                scount = self.get_signed_count(line, count)
                self.added.append(scount)
                count += 1
            elif first == '-':
                # here we get the line number where the deleted lines
                # should be in the new file
                scount = self.get_signed_count(line, count)
                self.deleted.append(scount)
                self.count_minus(count + 1)

    def parse_hunks(self, line):
        self._condition(lambda x: x.startswith('@'))
        for line in self.get_lines:
            if line is None:
                break
            self.parse_hunk(line)

    def get_touched(self):
        '''
        Negative line numbers are for empty
        lines (i.e. whites, comments, ...)
        Of course we keep positive lines
        but we keep common lines which aren't both negative
        if added=[1,2,3,4,-5,-6,-7,8,10] and deleted=[4,5,6,-7,9,-10]
        then res_a=[1,2,3,8], res_d=[9], res_t=[4,5,6,10]
        '''
        added = set(self.added)
        deleted = set(self.deleted)

        def use_line(x):
            return not self.skip_comments or x > 0

        touched = set(abs(x) for x in added
                      if (use_line(x) and {x, -x} & deleted))
        touched |= set(abs(x) for x in deleted
                       if (use_line(x) and {x, -x} & added))
        added = [x for x in added if use_line(x) and x not in touched]
        deleted = [x for x in deleted if use_line(x) and x not in touched]
        touched = list(sorted(touched))
        added = list(sorted(added))
        deleted = list(sorted(deleted))

        return added, deleted, touched

    def get_changes(self):
        for line in self.get_lines:
            if line.startswith('new file'):
                self.skip_new_file()
                break
            elif line.startswith('deleted file'):
                self.skip_deleted_file()
                break
            elif line.startswith('diff --git a/') or line.startswith('diff -r '):
                return
            else:
                self.skip_useless()
                line = self.line()
                if line.startswith('@'):
                    self.parse_hunks(line)
                break

        if self.added or self.deleted:
            added, deleted, touched = self.get_touched()
            self.results[self.filename] = {'added': added,
                                           'deleted': deleted,
                                           'touched': touched,
                                           'new': False}

    def parse(self):
        try:
            while self.next_diff():
                if self.get_files():
                    self.move()
                    self.get_changes()
                else:
                    self.move()
        except StopIteration:
            pass
        return self.results


if __name__ == '__main__':
    description = 'Get changed line in a patch'
    parser = argparse.ArgumentParser(description=description)
    url = 'https://hg.mozilla.org/mozilla-central/raw-rev'
    parser.add_argument('-r', '--revision', dest='rev',
                        help='revision')
    parser.add_argument('-u', '--base-url', dest='url',
                        default=url,
                        help='base url to retrieve the patch')
    parser.add_argument('-s', '--chunk-size', dest='chunk_size',
                        default=1000000, type=int,
                        help='chunk size')
    parser.add_argument('-f', '--file', dest='file', default='',
                        help='diff file')
    parser.add_argument('-n', '--lines-for-new', dest='lines_for_new', action='store_true',
                        help='add line number for new files')
    args = parser.parse_args()

    if args.file:
        res = Patch.parse_file(args.file, add_lines_for_new=args.lines_for_new)
    else:
        res = Patch.parse_changeset(args.url,
                                    args.rev,
                                    chunk_size=args.chunk_size,
                                    add_lines_for_new=args.lines_for_new)

    pprint(res)
