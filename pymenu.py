#!/usr/bin/env python

"""Simple CLI menu framework.

A simple CLI menu framework that uses json definition files to define menu
structure.
"""

import io
import json

class Menu(object):
  """CLI Menu object"""

  def __init__(self, path, error_message=None):
    """Initialise a menu object.

    :param path: Relative or absolute path to a root menu file
    :param error_message: Error message to show to user on invalid option
    """
    self.root_path = path
    self.error_message = error_message

    with io.open(self.root_path, 'r') as fn:  # open file specfying menu hierarchy
      self.menu = json.loads(fn.read())  # convert json file to Python objects

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
      items = sub_menu['items']

      option = -1

      # loop while not exiting
      while (option != 0):
        # loop until valid user input is retrieved
        while (option not in range(1,len(items) + 1)) and (option != 0):
          # print test header
          print('---- {} ----\n'.format(sub_menu['name']))

          # print test options
          for i, item in enumerate(items):
            item = item['menu'] if 'menu' in item else item['function']
            print(' [{}] {}'.format(i + 1, item['name'].title()))

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
    else:
      function = menu['function']

      name = function['name']
      func = function['func'] if 'func' in function else self._format_menu_to_func(name)
      args = function['args']

      mod = __import__(function['module'])  # get module object
      func = getattr(mod, func)  # get function object

      return func(*args)  # call function with arguments

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
