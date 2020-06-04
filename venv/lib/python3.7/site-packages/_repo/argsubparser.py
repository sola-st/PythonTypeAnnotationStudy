# coding:utf-8


import sys
import argparse

def add_default(self, star=False):
    if star:
        self._star_default = star
    self.help += '(default: %(default)s)'
    return self

class ArgumentAndSubParser(argparse.ArgumentParser):
    """enhanced ArgumentParser

    - enable decorating of actions to suppress password defaults:
        add_argument('--passwd', default='abc123').star_default = True
    """
    def __init__(self, *args, **kw):
        if not kw.get('formatter_class'):
            kw['formatter_class'] = PasswordHelpFormatter
        super(ArgumentAndSubParser, self).__init__(*args, **kw)
        if sys.version_info < (3,):
            self.register('action', 'parsers', SubParsersAction)
        self._sub_parsers = None
        argparse.Action.add_default = add_default

    def add_sub_parser(self, name, help=None, aliases=None, cmd=None):
        # first sets up subparsers if necessary
        if hasattr(name, 'name'):
            cmd = name
            name = name.name
        if cmd:
            if not help:
                help = getattr(cmd, 'help', None)
            if not aliases:
                aliases = getattr(cmd, 'aliases', None)
        if self._sub_parsers is None:
            self._sub_parsers = self.add_subparsers(
                title='sub-commands',
                dest="subparser_name", help='sub-command help')
        sp = self._sub_parsers.add_parser(
            name, aliases=aliases, help=help,
            formatter_class=PasswordHelpFormatter,
        )
        if cmd:
            sp.set_defaults(func=cmd)
            # do not try except for attribute error, which might occur deep down
            if hasattr(cmd, 'add_arguments'):
                cmd.add_arguments(sp)
        return sp


class SubParsersAction(argparse._SubParsersAction):
    """support aliases, based on differences of 3.3 and 2.7
    """
    class _AliasesChoicesPseudoAction(argparse.Action):

        def __init__(self, name, aliases, help):
            metavar = dest = name
            if aliases:
                metavar += ' (%s)' % ', '.join(aliases)
            sup = super(SubParsersAction._AliasesChoicesPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help,
                         metavar=metavar)

    def add_parser(self, name, **kwargs):
        # remove aliases and help kwargs so orginal add_parser does not get them
        aliases = kwargs.pop('aliases', ())
        help = kwargs.pop('help', None)
        parser = argparse._SubParsersAction.add_parser(self, name, **kwargs)

        if help is not None:
            choice_action = self._AliasesChoicesPseudoAction(name, aliases, help)
            self._choices_actions.append(choice_action)
        if aliases is not None:
            for alias in aliases:
                self._name_parser_map[alias] = parser

        return parser

class PasswordHelpFormatter(argparse.HelpFormatter):
    def _expand_help(self, action):
        params = dict(vars(action), prog=self._prog)
        for name in list(params):
            if params[name] is argparse.SUPPRESS:
                del params[name]
        for name in list(params):
            if hasattr(params[name], '__name__'):
                params[name] = params[name].__name__
        if params.get('choices') is not None:
            choices_str = ', '.join([str(c) for c in params['choices']])
            params['choices'] = choices_str
        if hasattr(action, '_star_default'):
            if params.get('default') is not None:
                # you can update params, this will change the default, but we
                # are printing help only
                params['default'] = '*' * len(params['default'])
        return self._get_help_string(action) % params

