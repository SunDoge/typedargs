from argparse import Action, ArgumentParser, Namespace
from typing import TypeVar, Union, Optional, Any, Iterable, List, Tuple
from dataclasses import dataclass
import logging

__version__ = '0.2.1'

LOGGER = logging.getLogger(__name__)


class TypedArgsOld:
    _parser: ArgumentParser
    _args: Namespace

    def parse_args_from(self, parser: ArgumentParser):
        self._parser = parser
        self._args = self._parser.parse_args()
        self._assign_args()

    def parse_known_args_from(self, parser: ArgumentParser):
        self._parser = parser
        self._args, _ = self._parser.parse_known_args()
        self._assign_args()

    def _assign_args(self):

        for key, value in self.__dict__.items():
            if isinstance(value, Action):
                # Get arg name from Action
                dest = value.dest
                self.__dict__[key] = self._args.__dict__[dest]

    def __contains__(self, key):
        """
        Copy from Namespace
        """
        return key in self.__dict__

    def __repr__(self):
        return str(self._args)


"""
This type alias is added to fool PyCharm.
"""
T = TypeVar('T')
ArgType = Union[Action, T]


@dataclass
class TypedArgs:
    parser: ArgumentParser = ArgumentParser()

    @classmethod
    def from_args(cls, args: Optional[List[str]] = None, namespace: Optional[Namespace] = None):
        typed_args = cls()
        typed_args.add_arguments()
        typed_args.parse_args(args=args, namespace=namespace)
        return typed_args

    @classmethod
    def from_known_args(cls, args: Optional[List[str]] = None, namespace: Optional[Namespace] = None):
        typed_args = cls()
        typed_args.add_arguments()
        typed_args.parse_known_args(args=args, namespace=namespace)
        return typed_args

    def add_arguments(self):
        for name, annotation in self.__annotations__.items():
            self.add_argument(name, annotation)

    def add_argument(self, name: str, annotation: Any):
        phantom_action: PhantomAction = getattr(self, name)

        print('phantom action:', phantom_action)
        if phantom_action.option_strings[0].startswith('-'):  # optional
            self.parser.add_argument(
                *phantom_action.option_strings,
                action=phantom_action.action,
                nargs=phantom_action.nargs,
                const=phantom_action.const,
                default=phantom_action.default,
                type=annotation,  # use annotated type
                choices=phantom_action.choices,
                required=phantom_action.required,
                help=phantom_action.help,
                metavar=phantom_action.metavar,
                dest=name,  # use attribute name
            )
        else:
            # No dset
            # No required
            self.parser.add_argument(
                phantom_action.option_strings[0],  # positional arg has only one str input
                action=phantom_action.action,
                nargs=phantom_action.nargs,
                const=phantom_action.const,
                default=phantom_action.default,
                type=annotation,  # use annotated type
                choices=phantom_action.choices,
                help=phantom_action.help,
                metavar=phantom_action.metavar,
            )

    def parse_args(self, args: Optional[List[str]] = None, namespace: Optional[Namespace] = None):
        parsed_args = self.parser.parse_args(args=args, namespace=namespace)
        self.update_arguments(parsed_args)

    def parse_known_args(self, args: Optional[List[str]] = None, namespace: Optional[Namespace] = None):
        parsed_args, _ = self.parser.parse_known_args(args=args, namespace=namespace)
        self.update_arguments(parsed_args)

    def update_arguments(self, parsed_args: Namespace):
        for name in self.__annotations__.keys():
            value = getattr(parsed_args, name)
            setattr(self, name, value)


@dataclass
class PhantomAction:
    option_strings: Tuple[str, ...]
    action: Optional[str] = None
    nargs: Union[int, str, None] = None
    const: Optional[Any] = None
    default: Optional[Any] = None
    choices: Optional[Iterable] = None
    required: Optional[bool] = None
    help: Optional[str] = None
    metavar: Optional[str] = None


def add_argument(
        *option_strings: Union[str, Tuple[str, ...]],
        action: Optional[str] = None,
        nargs: Union[int, str, None] = None,
        const: Optional[Any] = None,
        default: Optional[Any] = None,
        choices: Optional[Iterable] = None,
        required: Optional[bool] = None,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
):
    # if type(option_strings) == str:
    #     option_strings = [option_strings]
    print('locals:', locals())
    return PhantomAction(**locals())
