# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_vanity.ipynb.

# %% auto 0
__all__ = ['guess_bech32', 'guess_hex', 'hex_chars', 'npub_chars', 'vanity_notifyr', 'expected_performance', 'gen_vanity_pubkey']

# %% ../nbs/04_vanity.ipynb 5
import time
import secrets
import secp256k1
import functools
from typing import Union
from .nostr import PrivateKey
from .notifyr import notifyr
from nostr import bech32

# %% ../nbs/04_vanity.ipynb 6
def _guess_bytes():
    privkey_bytes = secrets.token_bytes(32) 
    sk = secp256k1.PrivateKey(privkey_bytes)
    pubkey_bytes = sk.pubkey.serialize()[1:]
    return privkey_bytes, pubkey_bytes

def _make_bech32(pubkey_bytes):
    converted_bits = bech32.convertbits(pubkey_bytes, 8, 5)
    pubkey = bech32.bech32_encode('npub', converted_bits, bech32.Encoding.BECH32)
    return pubkey

def _make_hex(pubkey_bytes):
    return pubkey_bytes.hex()

# %% ../nbs/04_vanity.ipynb 8
def _guess_vanity(make_format, startswith=''):
    privkey_bytes, pubkey_bytes = _guess_bytes()
    pubkey_hex = make_format(pubkey_bytes)
    if pubkey_hex.startswith(startswith):
        return privkey_bytes.hex(), pubkey_hex
    else:
        return None, None


# %% ../nbs/04_vanity.ipynb 9
guess_bech32 = functools.partial(_guess_vanity, make_format=_make_bech32)
guess_hex = functools.partial(_guess_vanity, make_format=_make_hex)


# %% ../nbs/04_vanity.ipynb 13
def _time_guess(guesser):
    """get a timed assessment of a guess

    Parameters
    ----------
    guesser : function
        either `guess_npub` or `guess_hex`

    Returns
    -------
    float
        time in seconds
    """
    start = time.perf_counter()
    pub = guesser(startswith=' ')
    if pub is None:
        pass
    end = time.perf_counter()
    interval = end - start
    return interval

def _get_guess_time(guesser, n_guesses=1e4):
    """estimate a guess rate

    Parameters
    ----------
    guesser : function
        either `guess_npub` or `guess_hex`
    n_guesses : float, optional
        number of guesses to make for estimation, by default 1e4

    Returns
    -------
    float
        time in seconds
    """
    n_guesses = int(n_guesses)
    t = sum([_time_guess(guesser) for _ in range(n_guesses)]) / n_guesses
    return t

# %% ../nbs/04_vanity.ipynb 17
import math

# %% ../nbs/04_vanity.ipynb 18
def _expected_guesses_by_char(options: Union[str,list], num_char: int) -> float:
    """return an average number of guesses it would take to guess
    a pattern based on the number of characters in the pattern and
    the number of character options in the random output

    Parameters
    ----------
    options : list or str
        a set of characters as a str or list that are options for
        guessing
    num_char : int
        the number of characters in the pattern

    Returns
    -------
    float
        the expected number of guesses required to match the pattern
    """
    p = 1 / len(options)
    return (p ** -num_char - 1)/ (1 - p)

def _expected_chars_by_time(options: Union[str,list], num_guesses: int) -> float:
    """the length of pattern you might expect to be able to guess given a
    certain number of guesses.

    Parameters
    ----------
    options : list or str
        a set of characters as a str or list that are options for
        guessing
    num_guesses : int
        the total number of guesses at a pattern

    Returns
    -------
    float
        th
    """
    p = 1 / len(options)
    n = - math.log(1 + (num_guesses * (1 - p))) / math.log(p)
    return n

def _expected_time(options: Union[str,list], num_char: int, time_per_guess: float) -> float:
    """the expected amount of time it would take to guess a pattern with a certain
    length based on the average time per guess and the character options

    Parameters
    ----------
    options : list or str
        a set of characters as a str or list that are options for
        guessing
    num_char : int
        the number of characters in the pattern
    time_per_guess : float
        averge time per guess in seconds

    Returns
    -------
    float
        the expected amount of time needed to guess the pattern
    """
    n_guess = _expected_guesses_by_char(options, num_char)
    time_seconds = n_guess * time_per_guess
    return time_seconds

hex_chars = 'abcdef0123456789'
npub_chars = '023456789acdefghjklmnpqrstuvwxyz'


# %% ../nbs/04_vanity.ipynb 19
def _average_char_by_time(options: Union[str,list], time_per_guess: float) -> None:
    """print an average number of characters you would expect to be
    able to guess for certain time periods based on character options
    and the average time per guess

    Parameters
    ----------
    options : list or str
        a set of characters as a str or list that are options for
        guessing
    time_per_guess : float
        the average time elapsed per guess
    """
    seconds_in_month = 60 * 60 * 24 * 30.5
    seconds_in_day = 60 * 60 * 24
    seconds_in_hour = 60 * 60
    seconds_in_minute = 60

    guesses_per_month = seconds_in_month / time_per_guess
    guesses_per_day = seconds_in_day / time_per_guess
    guesses_per_hour = seconds_in_hour / time_per_guess
    guesses_per_minute = seconds_in_minute / time_per_guess
    guesses_per_second = 1 / time_per_guess

    guesses = [guesses_per_second, guesses_per_minute,\
               guesses_per_hour, guesses_per_day, guesses_per_month]

    expected_chars = [_expected_chars_by_time(options, g) for g in guesses]
    results = zip(['one second', 'one minute', 'one hour', 'one day', 'one month'],
                   expected_chars)
    for t, c in results:
        print(f'In {t} you can expect to get {c} characters on average')

def _average_time_by_char(options: Union[str,list], time_per_guess: float) -> None:
    """print an average elapsed time for a range of pattern lengths

    Parameters
    ----------
    options : Union[str,list]
        a set of characters as a str or list that are options for
        guessing
    time_per_guess : float
        the average time elapsed per guess
    """
    for n in range(20):
        n += 1
        t = _expected_time(options, n, time_per_guess)
        print(f'{n} characters: it might take {t} seconds')



# %% ../nbs/04_vanity.ipynb 23
def expected_performance():
    print(
        '''This is a random guessing process - estimations are an average, but the actual
        time it takes to find a key could be significantly more or less than the estimate!
        Please keep that in mind when choosing an option.
        ''')
    print('hex:')
    time_per_guess_hex = _get_guess_time(guesser=guess_hex)
    _average_char_by_time(hex_chars, time_per_guess_hex)
    print('\n')
    _average_time_by_char(hex_chars, time_per_guess_hex)
    print('\n')

    print('npub:')
    time_per_guess_bech32 = _get_guess_time(guesser=guess_bech32)
    _average_char_by_time(npub_chars, time_per_guess_bech32)
    print('\n')
    _average_time_by_char(npub_chars, time_per_guess_bech32)
    print('\n')

    

# %% ../nbs/04_vanity.ipynb 26
def gen_vanity_pubkey(startswith: str, style='hex') -> PrivateKey:
    """randomly generate private keys until one matches the desire
    startswith for an npub or hex

    Parameters
    ----------
    startswith : str
        characters that the public key should start with. More chars
        means longer run time
    style : str, optional
        'npub' or 'hex' - npub is more commonly displayed on apps
        while hex is the true base private key with no encoding,
        by default 'hex'

    Returns
    -------
    PrivateKey
        returns a private key object
    """
    pubkey = None
    if style == 'npub':
        if not all(c in npub_chars for c in startswith):
            raise ValueError(f'character of selection not '
                              'in npub pattern ({npub_chars})')
        time_per_guess = _get_guess_time(guess_bech32)
        t = _expected_time(npub_chars, len(startswith), time_per_guess)
        startswith = f'npub1{startswith}'
    else:
        if not all(c in hex_chars for c in startswith):
            raise ValueError(f'character of selection not in '
                              'hex pattern ({hex_chars})')
        time_per_guess = _get_guess_time(guess_hex)
        t = _expected_time(hex_chars, len(startswith), time_per_guess)
    print(f'It might take {int(t)} seconds to find a {style} pubkey that starts with '
          f'{startswith}. Note that this is a very rough estimate and due '
          'to the random nature of finding vanity keys it could take MUCH '
          'longer.')
    while pubkey is None:
        if style == 'npub':
            privkey_hex, pubkey = guess_bech32(startswith=startswith)
        else:
            privkey_hex, pubkey = guess_hex(startswith=startswith)
    return PrivateKey.from_hex(privkey_hex)

# %% ../nbs/04_vanity.ipynb 35
vanity_notifyr = notifyr(gen_vanity_pubkey)
