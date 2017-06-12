#!/usr/bin/env python  
# -*- coding: utf-8 -*-

from app.block.key import action as keyaction


def main():
    print keyaction.addr_to_hash160("1Ad57C78eoqL8x5e9H65bWHqbeQwcnCLpC", True)
    pass


if __name__ == '__main__':
    main()
