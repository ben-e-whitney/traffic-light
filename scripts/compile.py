import argparse
import csv
import datetime
import enum
import itertools
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
    yield {
        LightState.ON: LightSwitch.ON,
        LightState.OFF: LightSwitch.OFF,
    }[state]
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

TimedSwitch = tuple[datetime.timedelta, LightSwitch]

def timed_switches(
        durations: typing.Iterable[datetime.timedelta],
        switches: typing.Iterable[typing.Optional[LightSwitch]]
) -> typing.Iterator[TimedSwitch]:
    '''
    Generate timed light switches.

    Parameters
    ----------
    durations
        Durations for temporal blocks.
    switches
        Switches to make at the beginning of the corresponding temporal block.

    Yields
    ------
    datetime.timedelta
        Time since start of first block.
    switch
        Switch to make at the time.
    '''

    time: datetime.timedelta
    switch: typing.Optional[LightSwitch]
    for time, switch in zip(
            itertools.accumulate(durations, initial=datetime.timedelta()),
            switches
    ):
        if switch is not None:
            yield time, switch

TimedCall = tuple[datetime.timedelta, str]

def timed_calls(
        timed_switches: typing.Iterable[TimedSwitch],
        *,
        on: str,
        off: str
) -> typing.Iterable[tuple[datetime.timedelta, str]]:
    '''
    Generated timed function calls.

    Parameters
    ----------
    timed_switches
        Switches to make and the times to make them at.
    on
        Function to call to make a `LightSwitch.ON` switch.
    off
        Function to call to make a `LightSwitch.OFF` switch.

    Yields
    ------
    TimedCall
        Function to call and time to call it at.
    '''

    calls: dict[LightSwitch, str] = {LightSwitch.ON: on, LightSwitch.OFF: off}

    time: datetime.timedelta
    switch: LightSwitch
    for time, switch in timed_switches:
        yield time, calls[switch]

def sorted_grouped_calls(
        *args: typing.Iterable[TimedCall]
) -> typing.Iterator[tuple[datetime.timedelta, tuple[str, ...]]]:
    '''
    Group function calls by (ordered) time.

    Parameters
    ----------
    *args
        Functions to call and times to call them at.

    Yields
    ------
    datetime.timedelta
        Time to call functions atl.
    tuple[str, ...]
        Functions to call at the time.
    '''

    first: typing.Callable[[TimedCall], datetime.timedelta] = \
        operator.itemgetter(0)
    second: typing.Callable[[TimedCall], str] = operator.itemgetter(1)

    time: datetime.timedelta
    group: typing.Iterator[TimedCall]
    for time, group in itertools.groupby(
            sorted(itertools.chain(*args), key=first),
            key=first
    ):
        yield time, tuple(map(second, group))

COLORS: tuple[str, ...] = ('green', 'yellow', 'red')

parser = argparse.ArgumentParser(
    description='generate controller code from a light pattern',
)
parser.add_argument(
    'patternfile',
    help='file containing light pattern',
)
parser.add_argument(
    'codefile',
    help='generated file containing controller code',
)
args = parser.parse_args()

with open(args.patternfile, 'r', newline='') as f, \
        open(args.codefile, 'w') as g:
    reader = csv.reader(f)
    durations: tuple[datetime.timedelta, ...] = tuple(
        datetime.timedelta(seconds=s) for s in map(float, next(reader))
    )
    time: datetime.timedelta
    calls: tuple[str, ...]
    for time, calls in sorted_grouped_calls(*(
            timed_calls(
                timed_switches(durations, light_switches(light_states(row))),
                on=f'turn_{color}_on',
                off=f'turn_{color}_off'
            ) for color, row in zip(COLORS, reader)
    )):
        g.write(str(time))
        g.write('\n')
        call: str
        for call in calls:
            g.write('    ')
            g.write(call)
            g.write('\n')
