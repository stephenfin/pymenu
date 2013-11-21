#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple CLI menu framework.

A simple CLI menu framework that uses json definition files to define menu
structure.
"""

from __future__ import with_statement

import os

try:
  import json
except ImportError:
  print('Failed to import the "json" module. JSON support will be disabled.')
  print('Please install simplejson using `pip`')
try:
  import yaml
except ImportError:
  print('Failed to import the "yaml" module. YAML support will be disabled.')
  print('Please install PyYAML using `pip`')


class Menu(object):
  """CLI Menu object"""
  def __init__(self, path, error_message=None):
    """Initialise a menu object.

    :param path: Relative or absolute path to a root menu file
    :param error_message: Error message to show to user on invalid option
    """
    self.root_path = path
    self.root_dir = os.path.dirname(path)
    self.error_message = error_message

    file_name, file_extension = os.path.splitext(self.root_path)

    with open(self.root_path, 'r') as fn:  # open file specfying menu hierarchy
      if file_extension == '.json':
        self.menu = json.load(fn.read())  # convert json file to Python objects
      elif file_extension == '.yaml':
        self.menu = yaml.load(fn.read())  # convert yaml file to Python objects
      else:  # unrecognised extension
        raise Exception(
          'Unrecognised file extension. pymenu only supports .json and .yaml files')

  def show(self):
    """Show a menu to a user.

    Show a interactive text menu to a user, containing a given list of
    options. Call associated function or sub menu for that option.

    :returns: None
    """
    if self.menu:
      self._handle_menu_request(self.menu)  # call handler on top level file

  def _handle_menu_request(self, menu):
    """Handle request to call a function or sub menu from a menu

    :param menu: a dictionary object representing a menu

    :returns: None
    """
    # called a menu item
    if 'menu' in menu:
      sub_menu = menu['menu']  # decend menu
      name = sub_menu['name']
      
      # dealing with imported menu
      if 'import' in sub_menu:
        path = os.path.join(self.root_dir, sub_menu['import'])
        import_menu = Menu(path)
        return import_menu.show()
      
      # implicitly dealing with normal menu
      items = sub_menu['items']

      option = -1

      # loop while not exiting
      while (option != 0):
        # loop until valid user input is retrieved
        while (option not in range(1,len(items) + 1)) and (option != 0):
          # print test header
          print('---- %s ----\n' % (sub_menu['name']))

          # print test options
          for i, item in enumerate(items):
            item = item['menu'] if 'menu' in item else item['function']
            print(' [%d] %s' % (i + 1, item['name'].title()))

          # print exit option
          print('\n [0] Exit')

          # get user input
          try:
            option = int(raw_input('\nPlease Enter an Option: '))
          except ValueError:  
            if self.error_message:
              print(self.error_message)
            continue  # just ignore invalid values and retry
          except KeyboardInterrupt:  # exit cleanly
            exit()

        # in loop hence break on ``exit`` rather than return
        if option == 0:
          break

        # recursive call to handle chosen menu/function
        self._handle_menu_request(items[option - 1])

        option = -1

    # called a function item
    elif 'function' in menu:
      function = menu['function']

      name = function['name']
      func = function['func'] if 'func' in function else self._format_menu_to_func(name)
      args = function['args'] if 'args' in function else [{}]
      args = dict((k,v) for d in args for (k,v) in d.items()) # merge dict list

      mod = __import__(function['module'])  # get module object
      func = getattr(mod, func)  # get function object

      return func(**args)  # call function with arguments
    
    # neither menu nor function, i.e. unrecognised option
    else:
      Exception('Incorrectly formatted file!')

    return

  def _format_menu_to_func(self, name):
    """Converts a menu name to a function menu.

    Converts a menu name to a function menu. This is useful in preventing
    having to enter two fields where one could be used. For example, a menu
    item with a name of 'Show Symbols For Tag', would call the function
    'show_symbols_for_tag'.

    This is intended to be overriden to support different function or menu
    naming standards (i.e. camelcase function names, function names with a
    prefix etc.)

    :param name: The menu name to be formatted

    :returns: The function name
    """
    # remove non-alpha, non-space characters, then split and rejoin with
    # underscores to remove duplicated whitespace
    return '_'.join(
      ''.join(c for c in name if c.isalnum() or c.isspace()).split()).lower()
