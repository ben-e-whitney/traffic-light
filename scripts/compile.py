import enum
import operator
import typing

class LightState(enum.Enum):
    '''
    Light powered state.
    '''

    ON = enum.auto()
    OFF = enum.auto()
    UNDETERMINED = enum.auto()

def light_states(row: typing.Iterable[str]) -> typing.Iterator[LightState]:
    '''
    Parse a sequence of light powered state specifications.

    Parameters
    ----------
    row
        Iterable of light powered state specifications.

    Yields
    ------
    LightState
        Parsed specification.
    '''

    state: str
    for state in map(operator.methodcaller('strip'), row):
        try:
            yield LightState.UNDETERMINED if not state else LightState[state]
        except KeyError:
            raise ValueError(
                f"Could not interpret '{state}' as a 'LightState'."
            )
