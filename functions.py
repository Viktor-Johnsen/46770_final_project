'''
This module contains axiliary functions used for the project in
the course Integrated Energy Grids
'''


def annuity(n, r):
    """ Calculate the annuity factor for an asset with lifetime n years and
    discount rate  r """

    if r > 0:
        return r/(1. - 1./(1.+r)**n)
    return 1/n
