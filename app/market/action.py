#!/usr/bin/env python  
# -*- coding: utf-8 -*-

# from app.market import market
from app import context as ctx


def advert_erase(product):
    """

    :param product:
    :type product: market.PyProduct
    :return:
    """
    product_hash = product.get_hash()
    with ctx.dictProductsLock:
        ctx.dictProducts.pop(product_hash, None)  # equal to del d[key]


def advert_insert(product):
    """

    :param product:
    :type product: market.PyProduct
    :return:
    :rtype bool
    """
    product_hash = product.get_hash()
    f_new = False
    f_updated = False
    with ctx.dictProductsLock:
        # Insert or find existing product
        tmp_product = ctx.dictProducts.find(product_hash, None)
        if tmp_product is None:
            f_new = True
            ctx.dictProducts[product_hash] = product
            tmp_product = product
        else:
            f_new = False

        if product.sequence > tmp_product.sequence:
            tmp_product = product
            f_updated = True

        return f_new or f_updated


def main():
    pass


if __name__ == '__main__':
    main()
