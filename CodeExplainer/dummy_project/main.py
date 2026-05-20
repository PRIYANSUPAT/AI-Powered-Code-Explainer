import os
import sys
from utils import helper_function
from models import User

def main():
    user = User("Alice")
    print(helper_function(user.name))

if __name__ == "__main__":
    main()
