# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pycnnum


def amount2cn(num, counting_type=pycnnum.COUNTING_TYPES[1],
              big=True, traditional=False, alt_zero=False, alt_two=False,
              use_zeros=True):
    result = pycnnum.num2cn(num, counting_type, big, traditional, alt_zero, alt_two, use_zeros)
    if result == '':
        result = '零'
    jiao, fen = 0, 0
    jiaofen_index = result.find('点')
    if jiaofen_index > -1:
        result = result[:jiaofen_index]
        num_str = str(num)
        jiaofen_index = num_str.find('.')
        try:
            jiao = int(num_str[jiaofen_index + 1:jiaofen_index + 2])
            fen = int(num_str[jiaofen_index + 2:jiaofen_index + 3])
        except:
            pass
    if jiao == 0 and fen > 0:
        return '%s元%s%s分' % (result, pycnnum.big_number_s[jiao], pycnnum.big_number_s[fen])
    elif jiao > 0 and fen == 0:
        return '%s元%s角' % (result, pycnnum.big_number_s[jiao])
    elif jiao > 0 and fen > 0:
        return '%s元%s角%s分' % (result, pycnnum.big_number_s[jiao], pycnnum.big_number_s[fen])
    else:
        return '%s元整' % result
