#!/usr/bin/env python

"""Example demonstrating use of pymenu"""

from pymenu import Menu

def hello_world(param1=None, param2=None):
  if param1 and param2:
    print('Here are the arguments I received:')
    print('\tParam 1: {0}'.format(param1))
    print('\tParam 2: {0}'.format(param2))
    print('\n')
  else:
    print('Hello, world! (No params :()')

if __name__ == '__main__':
  hello_world()


def show_menu():
  menu = Menu('menu_example.json')
  menu.show()


if __name__ == '__main__':
  show_menu()
