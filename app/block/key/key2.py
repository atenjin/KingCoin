#!/usr/bin/env python  
# -*- coding: utf-8 -*-
import ecdsa
import hashlib
import os
import random

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def generate_pri_key():
    return ''.join(['%x' % random.randrange(16) for x in range(0, 64)])


def base58encode(n):
    result = ''
    while n > 0:
        result = b58[n % 58] + result
        n /= 58
    return result


def base256decode(s):
    result = 0
    for c in s:
        result = result * 256 + ord(c)
    return result


def countLeadingChars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count


def base58CheckEncode(version, payload):  # payload is pri key
    s = chr(version) + payload
    # 在私钥的前面加上版本号
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    # checksum （所谓附加校验码，就是对私钥经过2次SHA-256运算，取两次哈希结果的前四字节），
    result = s + checksum  # result = version + pri_key + checksum
    # 后面添加压缩标志和附加校验码
    leadingZeros = countLeadingChars(result, '\0')
    # 关于countLeadingChars wiki上有说明 保留作leading zero用的
    # leadingZeros + hash(hash(version + pri_key + checksum))
    return '1' * leadingZeros + base58encode(base256decode(result))


# def base58CheckEncode(version, payload):
#     s = chr(version) + payload
# print 's len: ', len(s)
# print 's', s.encode('hex')
# print "source", binascii.b2a_hex(s) # binascii.b2a_hex把字符串转化成了每个字符对应的16位ascii码值
# checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
# print "checksum", binascii.b2a_hex(checksum)

def privateKeyToPublicKey(s):
    '''
    私钥经过椭圆曲线乘法运算，可以得到公钥。公钥是椭圆曲线上的点，
    并具有x和y坐标。公钥有两种形式：压缩的与非压缩的。
    早期比特币均使用非压缩公钥，现在大部分客户端默认使用压缩公钥。
    :param s:
    :return:
    '''
    sk = ecdsa.SigningKey.from_string(s.decode('hex'), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    return ('\04' + sk.verifying_key.to_string()).encode('hex')


def pubKeyToAddr(s):
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(s.decode('hex')).digest())
    return base58CheckEncode(0, ripemd160.digest())


def KeyToAddr(s):
    return pubKeyToAddr(privateKeyToPublicKey(s))


private_key = os.urandom(32).encode('hex')
# s 是 私钥
s = '0C28FCA386C7A227600B2FE50B7CAE11EC86D3BF1FBE471BE89827E19D72AA1D'
print base58CheckEncode(0x80, s.decode('hex'))
# 在私钥的前面加上版本号，后面添加压缩标志和附加校验码，
# （所谓附加校验码，就是对私钥经过2次SHA-256运算，取两次哈希结果的前四字节），
# 然后再对其进行Base58编码，就可以得到我们常见的WIF（Wallet import Format)格式的私钥。



# a = '18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725'
a = '418c1bfa9e03935335f1c248d29fc27019dff2bd06f37ecbeb1914f0cb099b96'
print 'a', len(a)
pub = privateKeyToPublicKey(a)
print len(pub)
print pub
print '\n'
s = '0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6'
print pubKeyToAddr(s)


def main():
    # pri_key = generate_pri_key()
    # print len(pri_key)
    # print pri_key
    # pri_key_hex = pri_key.decode('hex')
    # print len(pri_key_hex)
    # print pri_key_hex
    pass


if __name__ == '__main__':
    main()
