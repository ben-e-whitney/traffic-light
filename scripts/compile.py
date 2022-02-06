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

class LightSwitch(enum.Enum):
    '''
    Switch to make to light powered state.
    '''

    ON = enum.auto()
    OFF = enum.auto()

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

def light_switches(
        states: typing.Iterable[LightState]
) -> typing.Iterator[typing.Optional[LightSwitch]]:
    '''
    Generate switches from a sequence of light powered states.

    Parameters
    ----------
    states
        Iterable of light powered states.

    Yields
    ------
    typing.Optional[LightSwitch]
        Switches to effect the given sequence of light powered states.
    '''

    states_: typing.Iterator[LightState] = iter(states)
    try:
        state: LightState = next(states_)
    except StopIteration:
        raise ValueError("'LightState' iterable must be nonempty.")
    if state == LightState.UNDETERMINED:
        raise ValueError("First 'LightState' cannot be 'UNDETERMINED'.")
    yield state
    next_state: LightState
    for next_state in states_:
        if next_state == state or next_state == LightState.UNDETERMINED:
            yield None
        elif next_state == LightState.ON:
            yield LightSwitch.ON
        elif next_state == LightState.OFF:
            yield LightSwitch.OFF
        else:
            raise RuntimeError
        state = next_state
