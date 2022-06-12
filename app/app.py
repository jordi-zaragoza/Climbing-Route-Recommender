from lib.st_jzar import *

# This is the route recommender script
#
# I created a route recommender based on the features of the routes and the climber.
# by Jordi Zaragoza
#
# - Contact me if you want to colab -
# email: j.z.cuffi@gmail.com
# github: github.com/jordi-zaragoza


page_config()
sidebar()
title()


def main():
    form()
    recommendation()
    show_me_more()
    climber_info()
    reset()


if __name__ == "__main__":
    main()
