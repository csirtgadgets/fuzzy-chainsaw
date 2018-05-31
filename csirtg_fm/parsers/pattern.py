import copy
import re
import logging

from csirtg_fm.parsers import Parser
from csirtg_fm.utils.columns import get_indicator

logger = logging.getLogger(__name__)

class Pattern(Parser):

    def __init__(self, *args, **kwargs):
        super(Pattern, self).__init__(*args, **kwargs)

        self.pattern = self.rule.defaults.get('pattern')

        if self.rule.feeds[self.feed].get('pattern'):
            self.pattern = self.rule.feeds[self.feed].get('pattern')

        if self.pattern:
            self.pattern = re.compile(self.pattern)

        self.split = "\n"

        if self.rule.feeds[self.feed].get('values'):
            self.cols = self.rule.feeds[self.feed].get('values')
        else:
            self.cols = self.rule.defaults.get('values', [])

        self.defaults = self._defaults()

        if isinstance(self.cols, str):
            self.cols = self.cols.split(',')

    def process(self):
        count = 0
        with open(self.cache, 'rb') as cache:
            for l in cache.readlines():
                l = l.decode('utf-8')

                if self.ignore(l):  # comment or skip
                    continue

                l = l.rstrip()
                l = l.replace('\"', '')

                logger.debug(l)
                try:
                    m = self.pattern.search(l).groups()
                except ValueError as e:
                    continue
                except AttributeError as e:
                    continue

                i = get_indicator(m)

                if not i.itype:
                    logger.error("unable to parse line: \n%s" % l)
                    continue

                self.set_defaults(i)

                if self.cols:
                    for idx, col in enumerate(self.cols):
                        setattr(i, col, m[idx])

                logger.debug(i)

                yield i.__dict__()

                count += 1
                if self.limit and int(self.limit) == count:
                    return


Plugin = Pattern