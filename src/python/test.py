import os

import selenium_handler

def main():
  print(selenium_handler.init(os.getenv('username'), os.getenv('username'), 'Michigan'))

if __name__ == '__main__':
  main()
