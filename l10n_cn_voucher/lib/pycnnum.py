# -*- coding: utf-8 -*-
import sys

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

    # The MIT License (MIT)
    # Copyright (c) 2015 by Shuo Li (contact@shuo.li)
    #
    # Permission is hereby granted, free of charge, to any person obtaining a
    # copy of this software and associated documentation files (the "Software"),
    # to deal in the Software without restriction, including without limitation
    # the rights to use, copy, modify, merge, publish, distribute, sublicense,
    # and/or sell copies of the Software, and to permit persons to whom the
    # Software is furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    # DEALINGS IN THE SOFTWARE.

''' Chinese number <=> int/float conversion methods '''

__author__ = 'Shuo Li <contact@shuol.li>'
__version__ = '2015-08-06-11:35'

import re

if 'constants':
    COUNTING_TYPES = ['low', 'mid', 'high']

    number = u'零一二三四五六七八九'
    big_number_s = u'零壹贰叁肆伍陆柒捌玖'
    big_number_t = u'零壹貳參肆伍陸柒捌玖'

    unit_s = u'亿兆京垓秭穰沟涧正载'
    unit_t = u'億兆京垓秭穰溝澗正載'

    sunit_s = u'十百千万'
    sunit_t = u'拾佰仟萬'

    zero_alt = '〇'
    two_alts = ['两', '兩']

    positive = ['正', '正']
    negative = ['负', '負']
    point = ['点', '點']

chinese_number_string = list(set(
    number + big_number_s + big_number_t + \
    unit_s + unit_t + sunit_s + sunit_t + zero_alt + \
    ''.join(two_alts + positive + negative + point)))

if 'class definitions':

    class ChineseChar(object):

        def __init__(self, simplified, traditional):
            self.simplified = simplified
            self.traditional = traditional
            self.__repr__ = self.__str__

        def __str__(self):
            return self.simplified or 'None'

        def __repr__(self):
            return self.__str__()


    class ChineseNumberUnit(ChineseChar):

        def __init__(self, power, simplified, traditional, big_s, big_t):
            super(ChineseNumberUnit, self).__init__(simplified, traditional)
            self.power = power
            self.big_s = big_s
            self.big_t = big_t

        def __str__(self):
            return '10^{}'.format(self.power)

        @classmethod
        def create(cls, index, value, counting_type=COUNTING_TYPES[1], small_unit=False):

            if small_unit:
                return ChineseNumberUnit(power=index + 1,
                                         simplified=value[0], traditional=value[1], big_s=value[1], big_t=value[1])
            elif counting_type == COUNTING_TYPES[0]:
                return ChineseNumberUnit(power=index + 8,
                                         simplified=value[0], traditional=value[1], big_s=value[0], big_t=value[1])
            elif counting_type == COUNTING_TYPES[1]:
                return ChineseNumberUnit(power=(index + 2) * 4,
                                         simplified=value[0], traditional=value[1], big_s=value[0], big_t=value[1])
            elif counting_type == COUNTING_TYPES[2]:
                return ChineseNumberUnit(power=pow(2, index + 3),
                                         simplified=value[0], traditional=value[1], big_s=value[0], big_t=value[1])
            else:
                raise ValueError(
                    'Counting type should be in {0} ({1} provided).'.format(COUNTING_TYPES, counting_type))


    class ChineseNumberDigi(ChineseChar):

        def __init__(self, value, simplified, traditional, big_s, big_t, alt_s=None, alt_t=None):
            super(ChineseNumberDigi, self).__init__(simplified, traditional)
            self.value = value
            self.big_s = big_s
            self.big_t = big_t
            self.alt_s = alt_s
            self.alt_t = alt_t

        def __str__(self):
            return str(self.value)

        @classmethod
        def create(cls, i, v):
            return ChineseNumberDigi(i, v[0], v[1], v[2], v[3])


    class ChineseMath(ChineseChar):

        def __init__(self, simplified, traditional, symbol, expression=None):
            super(ChineseMath, self).__init__(simplified, traditional)
            self.symbol = symbol
            self.expression = expression
            self.big_s = simplified
            self.big_t = traditional


    CC, CNU, CND, CM = ChineseChar, ChineseNumberUnit, ChineseNumberDigi, ChineseMath


    class CountingSystem(object):
        pass


    class MathSymbols(object):
        def __iter__(self):
            for v in self.__dict__.values():
                yield v

if 'create systems':

    def create_system(counting_type=COUNTING_TYPES[1]):

        units = [CNU.create(i, v, counting_type, False) for i, v in enumerate(zip(unit_s, unit_t))]
        sunits = [CNU.create(i, v, small_unit=True) for i, v in enumerate(zip(sunit_s, sunit_t))]
        digits = [CND.create(i, v) for i, v in enumerate(zip(number, number, big_number_s, big_number_t))]
        digits[0].alt_s, digits[0].alt_t = zero_alt, zero_alt
        digits[2].alt_s, digits[2].alt_t = two_alts[0], two_alts[1]

        positive_cn = CM(positive[0], positive[1], '+', lambda x: x)
        negative_cn = CM(negative[0], negative[1], '-', lambda x: -x)
        point_cn = CM(point[0], point[1], '.', lambda x, y: float(str(x) + '.' + str(y)))
        system = CountingSystem()
        system.units = sunits + units
        system.digits = digits
        system.math = MathSymbols()
        system.math.positive = positive_cn
        system.math.negative = negative_cn
        system.math.point = point_cn

        return system


    systems = {ct: create_system(ct) for ct in COUNTING_TYPES}
    for ct in COUNTING_TYPES:
        systems[ct] = create_system(ct)


def cn2num(chinese_string, counting_type=COUNTING_TYPES[1]):
    def get_symbol(char, system):
        for u in system.units:
            if char in [u.traditional, u.simplified, u.big_s, u.big_t]:
                return u
        for d in system.digits:
            if char in [d.traditional, d.simplified, d.big_s, d.big_t, d.alt_s, d.alt_t]:
                return d
        for m in system.math:
            if char in [m.traditional, m.simplified]:
                return m

    def string2symbols(chinese_string, system):
        int_string, dec_string = chinese_string, ''
        for p in [system.math.point.simplified, system.math.point.traditional]:
            if p in chinese_string:
                int_string, dec_string = chinese_string.split(p)
                break
        return [get_symbol(c, system) for c in int_string], \
               [get_symbol(c, system) for c in dec_string]

    def correct_symbols(integer_symbols, system):

        ''' 一百八 to 一百八十, 一亿一千三百万 to 一亿 一千万 三百万'''

        if integer_symbols and isinstance(integer_symbols[0], CNU):
            if integer_symbols[0].power == 1:
                integer_symbols = [system.digits[1]] + integer_symbols

        if len(integer_symbols) > 1:
            if isinstance(integer_symbols[-1], CND) and isinstance(integer_symbols[-2], CNU):
                integer_symbols.append(CNU(integer_symbols[-2].power - 1, None, None, None, None))

        result = []
        unit_count = 0
        for s in integer_symbols:
            if isinstance(s, CND):
                result.append(s)
                unit_count = 0
            elif isinstance(s, CNU):
                current_unit = CNU(s.power, None, None, None, None)
                unit_count += 1

            if unit_count == 1:
                result.append(current_unit)
            elif unit_count > 1:
                for i in range(len(result)):
                    if isinstance(result[-i - 1], CNU) and result[-i - 1].power < current_unit.power:
                        result[-i - 1] = CNU(result[-i - 1].power + current_unit.power, None, None, None, None)
        return result

    def compute_value(integer_symbols):
        value = [0]
        for s in integer_symbols:
            if isinstance(s, CND):
                value[-1] += s.value
            elif isinstance(s, CNU):
                value[-1] *= pow(10, s.power)
                value.append(0)
        return sum(value)

    system = systems[counting_type]
    int_part, dec_part = string2symbols(chinese_string, system)
    int_part = correct_symbols(int_part, system)
    int_value = compute_value(int_part)
    dec_str = ''.join([str(d.value) for d in dec_part])
    if dec_part:
        return float('{0}.{1}'.format(str(int_value), dec_str))
    else:
        return int_value


def num2cn(num, counting_type=COUNTING_TYPES[1],
           big=False, traditional=False, alt_zero=False, alt_two=False,
           use_zeros=True):
    def get_value(value_string, use_zeros=True):

        striped_string = value_string.lstrip('0')

        # record nothing if all zeros
        if not striped_string:
            return []
        # record one digits
        elif len(striped_string) == 1:
            if use_zeros and len(value_string) != len(striped_string):
                return [system.digits[0], system.digits[int(striped_string)]]
            else:
                return [system.digits[int(striped_string)]]
        # recursively record multiple digits
        else:
            result_unit = [u for u in system.units if u.power < len(striped_string)][-1]
            result_string = value_string[:-result_unit.power]
            return get_value(result_string) \
                   + [result_unit] \
                   + get_value(striped_string[-result_unit.power:])

    system = systems[counting_type]
    units, sunits = system.units[:-len(sunit_s)], system.units[-len(sunit_s):]

    if isinstance(num, int):
        int_value = num
        dec_value = None
    elif isinstance(num, float):
        int_value = int(num)
        dec_value = num - int(num)

    int_string = str(int_value)
    dec_string = str(dec_value).split('.')[-1] if dec_value else ''

    result_symbols = get_value(int_string)
    dec_symbols = [system.digits[int(c)] for c in dec_string]
    if dec_string:
        result_symbols += [system.math.point] + dec_symbols

    if alt_two:
        liang = CND(2, system.digits[2].alt_s, system.digits[2].alt_t,
                    system.digits[2].big_s, system.digits[2].big_t)
        for i, v in enumerate(result_symbols):
            next_symbol = result_symbols[i + 1] if i < len(result_symbols) - 1 else None
            previous_symbol = result_symbols[i - 1] if i > 0 else None
            if isinstance(next_symbol, CNU) and isinstance(previous_symbol, CNU):
                if next_symbol.power != 1 and previous_symbol.power != 1:
                    result_symbols[i] = liang

    if big:
        attr_name = 'big_'
        if traditional:
            attr_name += 't'
        else:
            attr_name += 's'
    else:
        if traditional:
            attr_name = 'traditional'
        else:
            attr_name = 'simplified'

    result = ''.join([getattr(s, attr_name) for s in result_symbols])

    if alt_zero:
        result = result.replace(getattr(system.digits[0], attr_name), system.digits[0].alt_s)

    return result

if __name__ == '__main__':
    print('num:', cn2num('十'))
    print('num:', cn2num('一亿六点三'))
    c = num2cn(33212222222, counting_type='high', alt_two=True, big=True, traditional=True)
    print(c)
