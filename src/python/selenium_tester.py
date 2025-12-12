import selenium_handler
import time
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    # task_generator.init()
    # auto_pull_math.main()
    username = os.getenv('username')
    password = os.getenv('PASSWORD')
    selenium_handler.init(username, password,'Michigan')
    while True:
      time.sleep(1)



if __name__ == '__main__':
    main()
