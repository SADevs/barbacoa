# -*- coding: utf-8 -*-


class PackBaseException(Exception):
    '''
    Base exception where all of Pack's exceptions derive
    '''


class PackError(PackBaseException):
    '''
    General purpose pack exception to signal an error
    '''


class PackLoadError(PackBaseException):
    '''
    Exception raised when a pack module fails to load
    '''


class PackLookupError(PackBaseException):
    '''
    Exception raised when a pack module lookup fails
    '''
