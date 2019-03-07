import logging

import click
from proverkacheka.api import API
from proverkacheka.exceptions import ProverkachekaBaseException

from svoibudjetapi import app

logger = logging.getLogger(__name__)


@app.cli.command()
@click.argument('string')
def restore_qr_string(string: str):
    """Tries replace "?" by  numbers(0-9). STRING example:
    t=20190208T0846&s=89.99&fn=8712000101134301&i=126651&fp=160500???8&n=1"""
    api = API(
        username=app.config.get('PROVERKACHECKA_USER'),
        password=app.config.get('PROVERKACHECKA_PASS'),
    )

    parts = []
    count = 0
    for ch in string:
        if ch != '?':
            parts.append(ch)
        else:
            parts.append('{%d}' % count)
            count += 1
    pattern = ''.join(parts)
    finish = int('9' * count)

    for current in range(finish):
        chars = str(current).zfill(count)
        click.echo(f'{chars}/{finish}\r', nl=False)
        qr_string = pattern.format(*chars)
        try:
            valid = api.check_ticket(qr_string)
        except ProverkachekaBaseException as e:
            logger.warn(e)
        else:
            if valid:
                click.echo(qr_string)
                break
        current += 1
    else:
        click.echo('Not Found.')
