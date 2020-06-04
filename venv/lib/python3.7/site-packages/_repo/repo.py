
import sys
import os
import time
import subprocess
import json
import argparse

from ConfigParser import SafeConfigParser

import requests

from _repo.config import Config

from _repo._argcomplete import try_argcomplete, filescompleter
from _repo.argsubparser import ArgumentAndSubParser

def check_output(*args, **kwargs):
    """allow string or multiple args to be specified instead of list"""
    if isinstance(args[0], list):
        new_args = args
    else:
        if len(args) == 1 and isinstance(args[0], basestring):
            args = args[0].split()
        new_args = [args]
    string_in = kwargs.pop('input', None)
    expected_return_code = kwargs.pop('return_code', [])
    if not isinstance(expected_return_code, list):
        expected_return_code = [expected_return_code]
    #print 'string_in', string_in
    #print 'new_args', new_args
    # possible pop extra arguments for Popen
    # newargs.extend(kwargs.pop('args', [])
    process = subprocess.Popen(stdin=subprocess.PIPE if string_in else None,
            stdout=subprocess.PIPE, *new_args, **kwargs)
    output, unused_err = process.communicate(input=string_in)
    retcode = process.poll()
    if retcode and not retcode in expected_return_code:
        cmd = args[0]
        raise subprocess.CalledProcessError(retcode, cmd)
    return output
    #return subprocess.check_output(*new_args, **kwargs)

class BitbucketAPI(object):
    domain = 'bitbucket.org'
    def __init__(self, user_name=None, pass_word=None, verbose=0):
        self._auth = (user_name, pass_word)
        self._status = None
        self._verbose = verbose

    def _request(self, method, *url, **kw):
        self._status = None
        #authorization = kw.pop('auth', None)
        x = 'https://%s/api/1.0/' % (BitbucketAPI.domain) + '/'.join(url)
        if self._verbose > 0:
            print method, x, kw
        response = requests.api.request(method, x, **kw)
        assert isinstance(response, requests.Response)
        try:
            response.raise_for_status()
            data = self._parse_json(response.text)
        except requests.exceptions.HTTPError:
            self._status = response.status_code
            raise
        return data

    def _parse_json(self, jsonstr):
        class Obj(dict):  # ToDo make this global -> pickle
            pass

        # do not use object_hook, that is unordered
        def _object_pairs_hook(pairs):
            obj = Obj()
            for k, v in pairs:
                obj[str(k)] = v
                setattr(obj, str(k), v)
            return obj

        if not jsonstr.strip():
            return Obj()
        return json.loads(jsonstr, object_pairs_hook=_object_pairs_hook)

    def repositories(self, user_name=None):
        """defaults to logged in username"""
        user_name = user_name if user_name else self._auth[0]
        data = self._request('GET', 'users', user_name)
        return data.repositories
        #ret_val = []
        #for repository in  data.repositories:
        #    ret_val.append(repository.name)
        #    #print 'repo', repository['name']  # can use as dict or as object
        #return ret_val

    def repository_delete(self, repo_slug):
        self._request('DELETE', 'repositories', self._auth[0], repo_slug, auth=self._auth)

    def fork(self, repo_name, account_name, repo_slug, **kw):
        self._request('POST', 'repositories', account_name, repo_slug, 'fork',
                      data=dict(name=repo_name), auth=self._auth)

class HgRc(object):
    def __init__(self):
        self._abs_file_name = os.path.abspath('.hg/hgrc')
        self._conpar = conpar = SafeConfigParser()
        conpar.read(self._abs_file_name)

    def get(self, section, option):
        return self._conpar.get(section, option)

    def set(self, section, option, value):
        self._conpar.set(section, option, value)

    def save(self, verbose=0):
        if verbose > 0:
            self._conpar.write(sys.stdout)
        with open(self._abs_file_name, 'w') as fp:
            self._conpar.write(fp)

    def set_ssh_default_push(self, push_repo=None):
        pr = push_repo
        if not pr:
            pr = self.get('paths', 'default').replace('https://', 'ssh://hg@')
        self.set('paths', 'default-push', pr)

    def check_set_default_push(self):
        dp = 'default-push'
        try:
            dp_val = self.get('paths', dp)
        except:
            raise

    def get_user_repo_name(self):
        acc, rest = self.get('paths', 'default').split(Bitbucket.domain)
        return rest[1:].split('/')

class PushPopDirs(object):
    def __init__(self):
        self._push_pop_dirs = []

    def pushd(self, dir = None):
        if dir is not None:
            self._push_pop_dirs.append(os.getcwd())
            os.chdir(dir)
        else:
            raise NotImplementedError('need to specify target dir')

    def popd(self, i = -1):
        newdir = self._push_pop_dirs.pop(i)
        os.chdir(newdir)

#_bbhg = None
#def bbhg():
#    global _bbhg
#    if _bbhg is None:
#        _bbhg = BitbucketMercurial()
#    return _bbhg

class Github:
    def __init__(self):
        pass

    def __call__(self, repo, args):
        print 'github called', repo, args

    def add_arguments(self, sub_parser):
        """add optional arguments to sub_parser"""
        sp = sub_parser
        sp.add_argument('--fork', nargs='?')

class Bitbucket:
    name = 'bitbucket'
    aliases = ['bb']
    help = 'work on repository from bitbucket'
    domain = 'bitbucket.org'

    def __init__(self):
        self._repo = None

    def clone(self):
        args = self._repo._args
        repo_name = args.clone
        if '/' in repo_name:
            user_name, repo_name = repo_name.split('/', 1)
        else:
            raise NotImplementedError
        https = 'https://{}/{}/{}'.format(self.domain, user_name, repo_name)
        cmd = ['hg', 'clone', https]
        local_name = args.local_name
        if local_name:
            if os.path.sep not in local_name:
                local_name = os.path.join(args.repo_base, local_name)
            print 'local_name', local_name
        else:
            local_name = os.path.join(args.repo_base, repo_name)
        cmd.append(local_name)
        if False:
            if os.path.exists(local_name):
                print 'error: path [%s] already exists' % (local_name)
                sys.exit(1)
            print cmd
            check_output(cmd)
        self._repo.pushd(local_name)
        print 'os.getcwd', os.getcwd()
        push_repo = args.push_base + self.name + '/{}/{}'.format(user_name,
                                                                 repo_name)
        print 'push_repo', push_repo
        #self.create_repo_clone(push_repo, https)
        hgrc = HgRc()
        hgrc.set_ssh_default_push(push_repo)
        hgrc.save()
        self._repo.popd()

    def create_repo_clone(self, path, https):
        """try ssh to create remote dir and then ssh + https pull
        """
        _, _, login, remote_dir = path.split('/', 3)  # 3 x '/' before real path
        remote_dir = os.path.dirname(remote_dir)  # final segment from clone
        print remote_dir
        cmd = ['ssh', login, 'mkdir', '-p', remote_dir]
        print cmd
        check_output(cmd)
        cmd = ['ssh', login, 'cd', remote_dir, ';', 'hg', 'clone', https]
        #cmd = ['ssh', login, 'cd {} ; hg clone {}'.format(remote_dir, path.replace('ssh:', 'https:'))]
        print cmd
        check_output(cmd)

    # ToDo some routine to gather all commit comments from a specific branch and
    # write to commit.msg ?

    def create_pr_repo_from_branch(self):
        sub_dir = '.repo'
        args = self._repo._args
        user_name = args.username
        pass_word = args.password
        #branch_name = 'argcomplete'
        hgrc = HgRc()
        hgrc.check_set_default_push()
        org_user, repo_name = hgrc.get_user_repo_name()
        branch_name = check_output('hg', 'branch').strip()
        if branch_name == 'default':
            print 'branch_name should not be default'
            return
        with open('commit.msg') as fp:
            commit_comment = fp.read().strip() + '\n'
        print org_user, repo_name, branch_name
        print 'commit_comment', commit_comment
        #print hgrc.get('paths', 'default')

        fork_name = '{}_{}'.format(repo_name, branch_name)
        bb = BitbucketAPI(user_name, pass_word)
        res = check_output('hg', 'pull')
        print res
        try:
            res = check_output('hg merge -r default')
            #print res
        except subprocess.CalledProcessError as e:
            print e
            pass
        if True:
            diff_text = check_output('hg diff -r default') # | (cd .repo/pytest_argparse/;  patch -p1', shell=True)
        if not diff_text.strip():
            raise NotImplementedError('no differences found diffing with -r default')
        if True:
            #bb.repository.delete(fork_name)
            try:
                bb.repository_delete(fork_name)
            except requests.exceptions.HTTPError:
                if bb._status != 404:
                    raise
                print 'repository %s not found' % (fork_name)
            #bb.fork(fork_name, org_user, repo_name)
            bb.fork(fork_name, org_user, repo_name)
            res = check_output('rm', '-rf', '{}/{}'.format(sub_dir, fork_name))
            # check if fork is already finished
            found = False
            while not found:
                print 'trying to find', fork_name, 'in repositories'
                for repo in bb.repositories():
                    if repo.name == fork_name:
                        found = True
                        break
                time.sleep(1)
            for try_out in range(5):
                # clone the fork
                print 'cloning', fork_name, 'try_out', try_out + 1
                try:
                    res = check_output(
                        'hg', 'clone',
                        'https://{}/{}/{}'.format(self.domain, user_name, fork_name),
                        '{}/{}'.format(sub_dir, fork_name))
                    break
                except subprocess.CalledProcessError:
                    pass
                print 'sleeping'
                time.sleep(10)
        #print res
        # add push info to new .hgrc
        self._repo.pushd('{}/{}'.format(sub_dir, fork_name))
        print 'adding default-push to config'
        hgrc_file_name = '{}/{}/.hg/hgrc'.format(sub_dir, fork_name)
        temp_hgrc = HgRc()
        temp_hgrc.set_ssh_default_push()
        temp_hgrc.save()
        #conpar = SafeConfigParser()
        #conpar.read(hgrc_file_name)
        #default = conpar.get('paths', 'default')
        #conpar.set('paths', 'default-push', default.replace('https://', 'ssh://hg@'))
        #with open(hgrc_file_name, 'w') as fp:
        #    conpar.write(fp)
        # apply diff
        print 'diff_text', diff_text[:500]
        res = check_output('patch', '-p1', input = diff_text)
        print 'patched', res
        print 'adding'
        res = check_output('hg add')
        print 'added:', res
        print 'committing'
        res = check_output('hg', 'commit',  '-m', '{}: {}'.format(branch_name, commit_comment))
        print 'comitted:', res
        res = check_output('hg push')
        print 'pushed', res

        self._repo.popd()
        print 'done'

    def update_pr_from_branch(self):
        sub_dir = '.repo'
        args = self._repo._args
        user_name = args.username
        pass_word = args.password
        hgrc = HgRc()
        hgrc.check_set_default_push()
        org_user, repo_name = hgrc.get_user_repo_name()
        branch_name = check_output('hg', 'branch').strip()
        if branch_name == 'default':
            print 'branch_name should not be default'
            return
        with open('commit.msg') as fp:
            commit_comment = fp.read().strip() + '\n'
        print org_user, repo_name, branch_name
        print 'commit_comment', commit_comment
        #print hgrc.get('paths', 'default')

        fork_name = '{}_{}'.format(repo_name, branch_name)
        bb = BitbucketAPI(user_name, pass_word)
        if False:
            res = check_output('hg', 'pull')
            print res
            try:
                res = check_output('hg merge -r default')
                #print res
            except subprocess.CalledProcessError as e:
                print e
                pass
        unknown_files = []  # and not in dotted subdirs
        for line in check_output('hg status -u').splitlines():
            line = line.strip()
            if not line:
                continue
            #if (line) < 4: #  or line[2] == '.':
            #    continue
            line = line[2:]
            unknown_files.append(line)
        #print 'unknown_files', unknown_files
        if False:
            diff_text = check_output('hg diff -r default') # | (cd .repo/pytest_argparse/;  patch -p1', shell=True)
        else: # diff against previous commit
            cmd = ['diff', '-ru']
            for x in ".hg .repo *egg-info *.pyc __pycache__ .tox".split() + unknown_files:
                cmd.extend(['-x', x])
            cmd.extend(["{}/{}".format(sub_dir, fork_name), "."])
            try:
                diff_text = check_output(cmd, return_code=[0,1])
            except subprocess.CalledProcessError as e:
                print dir(e)
                assert e.returncode == 1
        if not diff_text.strip():
            raise NotImplementedError('no differences found diffing with -r default')
        print diff_text
        if False:
            #bb.repository.delete(fork_name)
            try:
                bb.repository_delete(fork_name)
            except requests.exceptions.HTTPError:
                if bb._status != 404:
                    raise
                print 'repository %s not found' % (fork_name)
            #bb.fork(fork_name, org_user, repo_name)
            bb.fork(fork_name, org_user, repo_name)
            res = check_output('rm', '-rf', '{}/{}'.format(sub_dir, fork_name))
            # check if fork is already finished
            found = False
            while not found:
                print 'trying to find', fork_name, 'in repositories'
                for repo in bb.repositories():
                    if repo.name == fork_name:
                        found = True
                        break
                time.sleep(1)
            for try_out in range(5):
                # clone the fork
                print 'cloning', fork_name, 'try_out', try_out + 1
                try:
                    res = check_output(
                        'hg', 'clone',
                        'https://{}/{}/{}'.format(self.domain, user_name, fork_name),
                        '{}/{}'.format(sub_dir, fork_name))
                    break
                except subprocess.CalledProcessError:
                    pass
                print 'sleeping'
                time.sleep(10)
        #print res
        # add push info to new .hgrc
        self._repo.pushd('{}/{}'.format(sub_dir, fork_name))
        print 'adding default-push to config'
        hgrc_file_name = '{}/{}/.hg/hgrc'.format(sub_dir, fork_name)
        temp_hgrc = HgRc()
        temp_hgrc.set_ssh_default_push()
        temp_hgrc.save()
        #conpar = SafeConfigParser()
        #conpar.read(hgrc_file_name)
        #default = conpar.get('paths', 'default')
        #conpar.set('paths', 'default-push', default.replace('https://', 'ssh://hg@'))
        #with open(hgrc_file_name, 'w') as fp:
        #    conpar.write(fp)
        # apply diff
        print 'diff_text', diff_text[:500]
        res = check_output('patch', '-p2', input = diff_text)
        print 'patched', res
        print 'adding'
        res = check_output('hg add')
        print 'added:', res
        print 'committing'
        res = check_output('hg', 'commit',  '-m', '{}: {}'.format(branch_name, commit_comment))
        print 'comitted:', res
        res = check_output('hg push')
        print 'pushed', res

        self._repo.popd()
        print 'done'

    def close_branch(self, reason):
        branch_name = check_output('hg', 'branch').strip()
        if branch_name == 'default':
            print 'branch_name should not be default'
            return
        check_output('hg', 'commit', '--close-branch', '-m', reason)
        check_output('hg', 'update', '-r', 'default')

    def __call__(self, repo):
        self._repo = repo
        print 'bitbucket called', repo._args
        if repo._args.clone:
            return self.clone()
        if repo._args.branch_close:
            return self.close_branch(repo._args.branch_close)
        elif repo._args.create_pr:
            return self.create_pr_repo_from_branch()
        elif repo._args.update_pr:
            return self.update_pr_from_branch()
        #if repo._args.test:
        #    return self.test()

    def add_arguments(self, sub_parser):
        """add optional arguments to sub_parser"""
        sp = sub_parser
        sp.add_argument(
            '--fork', action='store_true',
            help="""positional arguments: [user_name/]repo_name [dest_repo_name]
            default name of fork is repo_name""")
        #sp.add_argument('--dest')
        sp.add_argument(
            '--clone', metavar=('USER/REPO'),
            help="clone remote, init backup and push")
        sp.add_argument(
            '--local-name', metavar=('REPO'),
            help="""local repo name (default is remote name), if no path,
            create under repo-base""")
        sp.add_argument(
            '--create-pr', action='store_true',
            help="""clone clean, diff against default, patch on clean, commit""")
        sp.add_argument(
            '--update-pr', action='store_true',
            help="""diff against previous patch, commit""",)
        #sp.add_argument('--test', action='store_true', help=argparse.SUPPRESS)
        sp.add_argument(
            '--branch-close', metavar='TXT',
            help="""close a branch with %(metavar)s as reason""",)
        sp.add_argument(
            '--username',
            help="username to use for push to bitbucket.org "
        ).add_default()
        sp.add_argument('--password',
            help="password to use for push to bitbucket.org "
        ).add_default(star=True)

class Auto:
    name = 'auto'
    help = 'automatic repository and origin'
    def __init__(self):
        pass

    def __call__(self, repo, args):
        print 'auto called', repo, args

    def add_arguments(self, sub_parser):
        """add optional arguments to sub_parser"""
        sp = sub_parser

class QuerySet(set):
    def query_add(self, value):
        if value in self:
            return True
        self.add(value)
        return False


class Repo(PushPopDirs):
    def __init__(self, auto=True):
        PushPopDirs.__init__(self)
        self.config = None

    def parser_setup(self):
        self._arg_parser = parser = ArgumentAndSubParser()
        sp = parser.add_sub_parser(Auto())
        sp = parser.add_sub_parser(Bitbucket())
        sp = parser.add_sub_parser('github', aliases=['gh'], cmd=Github(),
                             help='work on repository from github')
        parser.add_argument(
            '--repo-base', default='/data1/src', metavar='DIR',
            help="directory for creating repositories (default: %(default)s)",
        )
        parser.add_argument(
            '--push-base', metavar='REMOTEDIR',
            help="""remote dir for pushing repos. If 'None' try to push to own
            account at provider of the upstream repo (default: %(default)s)""",
        )
        #parser.add_argument(
        #    '--foo',
        #    help="foo (default: %(default)s)",
        #)
        #parser.add_argument(
        #    'bar',
        #)

    def parser_parse(self, args=None):
        try_argcomplete(self._arg_parser)
        self.config = Config('repo')
        #self.config.write(sys.stdout)
        self.set_defaults()
        self._args = self._arg_parser.parse_args(args)
        if hasattr(self._args, 'func'):
            return self._args.func(self)
        else:
            return self.run()

    def set_defaults(self):
        parser = self._arg_parser
        self._set_section_defaults(parser, 'global')
        x = parser._subparsers
        assert isinstance(x, argparse._ArgumentGroup)
        #print type(x), repr(x)
        #for p in parser._get_positional_actions():
        progs = QuerySet()
        subparsers = {}  # aliases filtered out
        for sp in parser._subparsers._group_actions:
            if not isinstance(sp, argparse._SubParsersAction):
                continue
            for k, action in sp.choices.iteritems():
                if progs.query_add(action.prog):
                    continue
                #print k, sp.choices[k]
                #print action._get_optional_actions()
                self._set_section_defaults(action, k)

    def _set_section_defaults(self, parser, section):
        defaults = {}
        #try:
        #    actions = parser._get_optional_actions()
        #except:
        #    actions = parser._get_subactions()
        for action in parser._get_optional_actions():
            if isinstance(action, (argparse._HelpAction,
                                   argparse._VersionAction,
                                   #SubParsersAction._AliasesChoicesPseudoAction,
                                   )):
                continue
            #if section == 'bitbucket' and not isinstance(action, argparse._StoreAction):
            #    print type(action), repr(action)
            for x in action.option_strings:
                if not x.startswith('--'):
                    continue
                try:
                    # get value based on long-option (without --) store in .dest
                    defaults[action.dest] = self.config[section][x[2:]]
                except KeyError:  # not in config file
                    pass
                break  # only first --option
        #if section == 'bitbucket':
        #    print 'defaults', section, defaults
        parser.set_defaults(**defaults)

    def run(self):
        pass
