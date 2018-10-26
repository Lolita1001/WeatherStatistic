# -*- coding: utf-8 -*-
import datetime
import sys, os
import functools
import xml.dom.minidom as MD
import xml.etree.ElementTree as ET
import traceback


def recorder_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        input_args = [arg for arg in args]
        input_kwargs = [kwarg for kwarg in kwargs]
        timestamp = datetime.datetime.today().utcnow()
        try:
            ret_val = func(*args, **kwargs)
            return ret_val
        except Exception as f:
            print('error yep')
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_info = traceback.format_exception(exc_type, exc_value, exc_traceback, limit=10)
            fault = f.__traceback__.tb_next.tb_frame
            asdf = fault.f_locals.setdefault('self', None)
            local_variable = {key: fault.f_locals[key] for key in [key for key in fault.f_locals.keys()]}
            if 'self' in fault.f_locals.keys():
                local_variable['self'] = fault.f_locals['self'].__dict__ if fault.f_locals['self'] is not None else None
            blobal_variable = fault.f_globals
            with open('log.txt', 'a', encoding='utf-8') as file_handler:
                file_handler.write(f'{timestamp}\n')
                file_handler.write(f'Input args:\n{input_args}\n')
                file_handler.write(f'Input kwargs:\n{input_kwargs}\n')
                file_handler.write(f'Local variable:\n{local_variable}\n')
                file_handler.write(f'Global variable:\n{blobal_variable}\n')
                file_handler.write('Error:\n')
                [file_handler.write(f'{tb_step}\n') for tb_step in tb_info]
                file_handler.write('===========================================\n'*3+'\n\n\n')
    return wrapper
