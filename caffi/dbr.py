__all__ = ['format_dbr', 'dbr_size_n']

from datetime import datetime

# convert epics ca types to numpy data types
try:
    import numpy
    ctype2dtype = {
        'dbr_int_t'    : numpy.int16,
        'dbr_float_t'  : numpy.float32,
        'dbr_char_t'   : numpy.uint8,
        'dbr_enum_t'   : numpy.uint16,
        'dbr_long_t'   : numpy.int32,
        'dbr_double_t' : numpy.float64,
    }
    has_numpy = True
except ImportError:
    has_numpy = False

from ._ca import *

from .constants import *

#/*
# * DBR structure size in bytes
# */
def dbr_size_n(TYPE,COUNT):
    if COUNT <=0:
        return libca.dbr_size[TYPE]
    else:
        return libca.dbr_size[TYPE] + (COUNT-1) * libca.dbr_value_size[TYPE]

#/*
# * ptr to value given a pointer to the structure and the DBR type
# */
def dbr_value_ptr(PDBR, DBR_TYPE):
    return ffi.cast('char*', PDBR) + libca.dbr_value_offset[DBR_TYPE]

#
# Functions that convert from DBR structure to dict
#
def format_dbr_sts(cvalue, value):
    value['status'] = cvalue.status
    value['severity'] = cvalue.severity


def format_dbr_time(cvalue, value):
    timestamp_posix = cvalue.stamp.secPastEpoch + POSIX_TIME_AT_EPICS_EPOCH + cvalue.stamp.nsec / 1e9
    value['stamp'] = datetime.fromtimestamp(timestamp_posix)


def format_dbr_gr(cvalue, value):
    value['units'] = ffi.string(cvalue.units)
    value['upper_disp_limit'] = cvalue.upper_disp_limit
    value['lower_disp_limit'] = cvalue.lower_disp_limit
    value['upper_alarm_limit'] = cvalue.upper_alarm_limit
    value['upper_warning_limit'] = cvalue.upper_warning_limit
    value['lower_alarm_limit'] = cvalue.lower_alarm_limit
    value['lower_warning_limit'] = cvalue.lower_warning_limit


def format_dbr_ctrl(cvalue, value):
    value['upper_ctrl_limit'] = cvalue.upper_ctrl_limit
    value['lower_ctrl_limit'] = cvalue.lower_ctrl_limit


def format_dbr_enum(cvalue, value):
    no_str = cvalue.no_str
    value['no_str'] = no_str
    value['strs'] = [ffi.string(cstr) for cstr in cvalue.strs[:no_str]]


def format_plain_value(valueType, count, cvalue):
    if count == 1:
        value = ffi.cast(valueType+'*', cvalue)[0]
    else:
        cvalue = ffi.cast(valueType+'[%d]'%count, cvalue)

        if has_numpy:
            value = numpy.frombuffer(ffi.buffer(cvalue), dtype=ctype2dtype[valueType])
        else:
            value = list(cvalue)

    return value

def format_string_value(count, dbrValue):
    cvalue = ffi.cast('dbr_string_t*', dbrValue)
    if count == 1:
        value = ffi.string(cvalue[0])
    else:
        value = []
        for i in range(count):
            value.append(ffi.string(cvalue[i]))
    return value

def format_dbr(dbrType, count, dbrValue):
    """
    Convert the specified dbr data structure to Python dict

    :param dbrType: The data type, DBR_XXX
    :param count: The array element count
    :param dbrValue: A pointer of data of the specified type and number
    :return: A dict filled with the values from the C structure fields.

    """
    if dbrType == DBR_STRING:
        value = format_string_value(count, dbrValue)

    elif dbrType == DBR_INT:
        value = format_plain_value('dbr_int_t', count, dbrValue)

    elif dbrType == DBR_FLOAT:
        value = format_plain_value('dbr_float_t', count, dbrValue)

    elif dbrType == DBR_ENUM:
        value = format_plain_value('dbr_enum_t', count, dbrValue)

    elif dbrType == DBR_CHAR:
        value = format_plain_value('dbr_char_t', count, dbrValue)

    elif dbrType == DBR_LONG:
        value = format_plain_value('dbr_long_t', count, dbrValue)

    elif dbrType == DBR_DOUBLE:
        value = format_plain_value('dbr_double_t', count, dbrValue)

    elif dbrType == DBR_STS_STRING or dbrType == DBR_STS_STRING or dbrType == DBR_CTRL_STRING:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_string*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_string_value(count, dbrValue)

    elif dbrType == DBR_STS_INT:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_int*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_int_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_STS_FLOAT:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_float*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_float_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_STS_ENUM:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_enum*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_enum_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_STS_CHAR:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_char*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_char_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_STS_LONG:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_long*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_long_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_STS_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_double*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        value['value'] = format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_STRING:
        value = {}
        cvalue = ffi.cast('struct dbr_sts_string*', count, dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_string_value(count, dbrValue)

    elif dbrType == DBR_TIME_INT:
        value = {}
        cvalue = ffi.cast('struct dbr_time_int*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_int_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_FLOAT:
        value = {}
        cvalue = ffi.cast('struct dbr_time_float*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_float_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_ENUM:
        value = {}
        cvalue = ffi.cast('struct dbr_time_enum*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_enum_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_CHAR:
        value = {}
        cvalue = ffi.cast('struct dbr_time_char*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_char_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_LONG:
        value = {}
        cvalue = ffi.cast('struct dbr_time_long*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_long_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_TIME_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_time_double*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_time(cvalue, value)
        value['value'] = format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_INT:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_int*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['value'] = format_plain_value('dbr_int_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_FLOAT:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_float*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['precision'] = cvalue.precision
        value['value'] = format_plain_value('dbr_float_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_ENUM:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_enume*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_enum(cvalue, value)
        value['value'] = format_plain_value('dbr_enum_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_CHAR:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_char*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['value'] = format_plain_value('dbr_char_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_LONG:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_long*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['value'] = format_plain_value('dbr_long_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_GR_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_gr_double*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['precision'] = cvalue.precision
        value['value'] = format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_INT:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_int*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        format_dbr_ctrl(cvalue, value)
        value['value'] = format_plain_value('dbr_int_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_FLOAT:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_float*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['precision'] = cvalue.precision
        format_dbr_ctrl(cvalue, value)
        value['value'] = format_plain_value('dbr_float_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_ENUM:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_enum*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_enum(cvalue, value)
        value['value'] = format_plain_value('dbr_enum_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_CHAR:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_char*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        format_dbr_ctrl(cvalue, value)
        value['value'] = format_plain_value('dbr_char_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_LONG:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_long*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        format_dbr_ctrl(cvalue, value)
        value['value'] = format_plain_value('dbr_long_t', count, dbr_value_ptr(cvalue, dbrType))

    elif dbrType == DBR_CTRL_DOUBLE:
        value = {}
        cvalue = ffi.cast('struct dbr_ctrl_double*', dbrValue)
        format_dbr_sts(cvalue, value)
        format_dbr_gr(cvalue, value)
        value['precision'] = cvalue.precision
        format_dbr_ctrl(cvalue, value)
        value['value'] = format_plain_value('dbr_double_t', count, dbr_value_ptr(cvalue, dbrType))

    # It should never reach here
    else:
        value = None

    return value
