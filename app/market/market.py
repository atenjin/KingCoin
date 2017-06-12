#!/usr/bin/env python  
# -*- coding: utf-8 -*-

import os

from app import config as cfg, context as ctx
from app.base.serialize import *
from app.block.utils import cryptoutil
from app.db import db
from app.utils import timeutil, baseutil
from app.block.key import PyKey
from app.net import net


class PyUser(Serializable):
    def __init__(self):
        self.atoms_in = list()  # vector<ushort>
        self.atoms_new = list()  # vector<ushort>
        self.atoms_out = list()  # vector<ushort>
        self.links_out = list()  # vector<uint256>
        pass

    def set_null(self):
        self.atoms_in = list()  # vector<ushort>
        self.atoms_new = list()  # vector<ushort>
        self.atoms_out = list()  # vector<ushort>
        self.links_out = list()  # vector<uint256>

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_int(nVersion))
        s.write(ser_list(self.atoms_in, ser_func=ser_ushort))
        s.write(ser_list(self.atoms_new, ser_func=ser_ushort))
        s.write(ser_list(self.atoms_out, ser_func=ser_ushort))
        s.write(ser_list(self.links_out, ser_func=ser_uint256))
        return s.getvalue()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        if not (nType & SerType.SER_GETHASH):
            nVersion = deser_int(f)
        self.atoms_in = deser_list(f, deser_ushort)
        self.atoms_new = deser_list(f, deser_ushort)
        self.atoms_out = deser_list(f, deser_ushort)
        self.links_out = deser_list(f, deser_uint256)
        return self

    def get_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self), out_type=out_type)

    def get_atom_count(self):
        return len(self.atoms_in) + len(self.atoms_new)

    def add_atom(self, atom, origin):
        # Ignore duplicates
        if binary_search(self.atoms_in, atom) or self.atoms_new.index(atom):
            return
        # // instead of zero atom, should change to free atom that propagates,
        # // limited to lower than a certain value like 5 so conflicts quickly
        # The zero atom never propagates,
        # new atoms always propagate through the user that created them
        if atom == 0 or origin:
            self.atoms_in.append(atom)
            self.atoms_in.sort()
            if origin:
                self.atoms_out.append(atom)

        self.atoms_new.append(atom)
        if len(self.atoms_new) >= cfg.FLOW_THROUGH_RATE or len(self.atoms_out) == 0:
            # Select atom to flow through to vAtomsOut
            self.atoms_out.append(self.atoms_new[baseutil.get_rand(len(self.atoms_new))])
            # Merge vAtomsNew into vAtomsIn
            self.atoms_in.extend(self.atoms_new)
            self.atoms_in.sort()
            del self.atoms_new[:]

        pass

    pass


class PyReview(Serializable):
    def __init__(self):
        self.nVersion = 1
        self.hash_to = 0
        self.dict_value = dict()  # dict<str, str>
        self.pubkey_from = b''
        self.sig = b''

        # memory
        self.time = 0
        self.natoms = 0
        pass

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.nVersion = ser_int(f)
        nVersion = self.nVersion
        if not (nType & SerType.SER_DISK):
            self.hash_to = deser_uint256(f)
        self.dict_value = deser_dict(f, deser_str, deser_str)  # dict<str, str>
        self.pubkey_from = deser_str(f)
        if not (nType & SerType.SER_GETHASH):
            self.sig = deser_str(f)
        return self

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_int(self.nVersion))
        nVersion = self.nVersion
        if not (nType & SerType.SER_DISK):
            s.write(ser_uint256(self.hash_to))
        s.write(ser_dict(self.dict_value, ser_str, ser_str))
        s.write(ser_str(self.pubkey_from))
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_str(self.sig))
        return s.getvalue()

    def get_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self), out_type)

    def get_sig_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self, SerType.SER_GETHASH | SerType.SER_SKIPSIG), out_type)

    def get_user_hash(self, out_type=None):
        return cryptoutil.Hash(self.pubkey_from, out_type)

    def accept_review(self):
        """

        :return:
        :rtype bool
        """
        time = timeutil.get_time()  # timestamp
        # check signature
        if not PyKey.static_verify(self.pubkey_from, self.get_sig_hash(out_type='str'), self.sig):
            return False

        reviewdb = PyReviewDB()

        # Add review text to recipient
        reviews = reviewdb.read_reviews(self.hash_to)  # list<PyReview>
        reviews.append(self)
        reviewdb.write_reviews(self.hash_to, reviews)

        # Add link from sender
        user = PyUser()
        hash_from = cryptoutil.Hash(self.pubkey_from)
        reviewdb.read_user(hash_from)
        user.links_out.append(self.hash_to)
        reviewdb.write_user(hash_from, user)

        reviewdb.close()

        if not add_atoms_and_propagate(self.hash_to, user.atoms_out if len(user.atoms_out) > 0 else [0], False):
            return False
        return True

    pass


class PyProduct(Serializable):
    def __init__(self):
        self.nVersion = 1  # int
        self.addr = net.PyAddress()
        self.dict_value = dict()  # dict<str, str> keys=['title', 'price', 'seller', 'stars', 'category', 'description', 'date', 'instructions']
        self.dict_details = dict()  # dict<str, str>
        self.list_order_from = list()  # list<(str,str)>  <label:str, control:str>
        self.sequence = 0  # uint
        self.pubkey_from = b''
        self.sig = b''
        # disk only
        self.atoms = 0  # int
        # memory only
        self.set_sources = set()  # set<uint>
        pass

    def serialize(self, nType=0, nVersion=cfg.VERSION):
        s = StringIO()
        s.write(ser_int(self.nVersion))
        nVersion = self.nVersion
        s.write(self.addr.serialize(nType, nVersion))
        s.write(ser_dict(self.dict_value, ser_str, ser_str))
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_dict(self.dict_details, ser_str, ser_str))
            s.write(ser_strpair_list(self.list_order_from))
            s.write(ser_uint(self.sequence))
        s.write(ser_str(self.pubkey_from))
        if not (nType & SerType.SER_GETHASH):
            s.write(ser_str(self.sig))
        if nType & SerType.SER_DISK:
            s.write(ser_int(self.atoms))
        return s.getvalue()

    def deserialize(self, f, nType=0, nVersion=cfg.VERSION):
        f = wrap_to_StringIO(f)
        self.nVersion = deser_int(f)
        nVersion = self.nVersion
        self.addr = net.PyAddress()
        self.addr.deserialize(f, nType, nVersion)
        self.dict_value = deser_dict(f, deser_str, deser_str)
        if not (nType & SerType.SER_GETHASH):
            self.dict_details = deser_dict(f, deser_str, deser_str)
            self.list_order_from = deser_strpair_list(f)
            self.sequence = deser_uint(f)
        self.pubkey_from = deser_str(f)
        if not (nType & SerType.SER_GETHASH):
            self.sig = deser_str(f)
        if nType & SerType.SER_DISK:
            self.atoms = ser_int(f)
        return self

    def get_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self), out_type)

    def get_sig_hash(self, out_type=None):
        return cryptoutil.Hash(serialize_hash(self, SerType.SER_GETHASH | SerType.SER_SKIPSIG), out_type)

    def get_user_hash(self, out_type=None):
        return cryptoutil.Hash(self.pubkey_from, out_type)

    def check_signature(self):
        return PyKey.static_verify(self.pubkey_from, self.get_sig_hash(out_type="str"), self.sig)

    def check_product(self):
        """

        :return:
        :rtype bool
        """
        if not self.check_signature():
            return False
        # Make sure it's a summary product
        if len(self.dict_details) != 0 or len(self.list_order_from) != 0:
            return False

        # Look up seller's atom count
        reviewdb = PyReviewDB("r")
        user = reviewdb.read_user(self.get_user_hash())
        self.atoms = user.get_atom_count()
        reviewdb.close()

        #    ////// delme, this is now done by AdvertInsert
        #     //// Store to memory
        #     //CRITICAL_BLOCK(cs_mapProducts)
        #     //    mapProducts[GetHash()] = *this;
        return True

    pass


def add_atoms_and_propagate(user_start_hash, atoms, origin):
    """

    :param user_start_hash:  uint256
    :param atoms: list<ushort>
    :type atoms: list
    :param origin: flag
    :return:
    """
    reviewdb = PyReviewDB()
    dict_propagate_pair = (dict(), dict())
    dict_propagate_pair[0][user_start_hash] = atoms

    side = 0
    while not (len(dict_propagate_pair[side]) == 0):  # init [0] is atoms
        dict_from = dict_propagate_pair[side]
        dict_to = dict_propagate_pair[1 - side]
        for user_hash, receiveds in dict_from:
            # Read user
            user = reviewdb.read_user(user_hash)
            nin = len(user.atoms_in)
            nnew = len(user.atoms_new)
            nout = len(user.atoms_out)
            # Add atoms received
            for atom in receiveds:
                user.add_atom(atom, origin)
            origin = False
            # Don't bother writing to disk if no changes
            if len(user.atoms_in) == nin and len(user.atoms_new) == nnew:
                continue
            # Propagate
            if len(user.atoms_out) > nout:
                for h in user.links_out:
                    if h in dict_to:
                        dict_to[h].extend(user.atoms_out[nout:])
                    else:
                        dict_to[h] = user.atoms_out[nout:]
            # write back
            reviewdb.write_user(user_hash, user)
        del dict_from[:]

        side = 1 - side
        pass
    reviewdb.close()
    return True


class PyReviewDB(db.PyDB):
    def __init__(self, szmode="r+", f_txn=False):
        super(PyReviewDB, self).__init__("reviews.dat", szmode=szmode, f_txn=f_txn)

    def read_user(self, hash_from):
        return self._read(("user", hash_from), PyUser)

    def write_user(self, user_hash, user):
        self._write(("user", user_hash), user)

    def read_reviews(self, hash_to):
        ret = self._read(("reviews", hash_to))
        if ret is None:
            return []
        return deser_list(StringIO(ret), PyReview)

    def write_reviews(self, hash_to, reviews):
        self._write(("reviews", hash_to), ser_list(reviews))

    pass


def binary_search(l, value):
    lo, hi = 0, len(l) - 1
    while lo <= hi:
        mid = (lo + hi) / 2
        if l[mid] < value:
            lo = mid + 1
        elif value < l[mid]:
            hi = mid - 1
        else:
            return mid
    return -1


def main():
    # print (get_rand(100))
    pass


if __name__ == '__main__':
    main()
