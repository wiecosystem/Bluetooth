# Xiaomi's proprietary auth protocol

## Intro

Many xiaomi (or sub-brands of the mi ecosystem) uses a proprietary authentication mechanism. This is in fact from the Mi Home SDK, and i'm assuming xiaomi also provides MCU sample code for these OEMs so they can integrate easily into Mi Home.

There seems to be two kind of binding: "weak" and "strong". (these are only used for server binding, not for ble directly!)

## Known devices

Check `devices_list.csv`

## BLE Services and characteristics

* MI Service (uuid=fe95)
* * Token characteristic (uuid=0001)
* * Firmware version characteristic (uuid=0004)
* * Wifi AP SSID characteristic (uuid=0005)
* * Wifi AP Password characteristic (uuid=0006)
* * Event characteristic (uuid=0010)
* * Wifi UID characteristic (uuid=0011)
* * Wifi Status characteristic (uuid=0005)
* * Serial Number characteristic (uuid=0013)
* * Beacon Key characteristic (uuid=0014)

## Login protocol

* Note: tick lenght is always 4 bytes!
* Enable notifications for the token characteristic && check response
* Send `session_start` ('\xCD\x43\xBC\x00') to the event characteristic
* Should receive some data ('challenge') in a notify from the token characteristic
* Compute 'tick' = encrypt(token, challenge)
* Compute encryption key = token[0:4] ^ tick[0:4]
* `session_end` = '\x93\xBF\xAC\x09'
* Send challenge response (= encrypt(encryption key, `session_end`))
* Should receive a confirmation (`confirmmation`) in a notify from token characteristic
* To confirm, compare '\x36\x9A\x58\xC9' and encrypt(encryption key, confirmation)[0:4]

## Register protocol

* Enable notifications for the token characteristic && check reponse
* Send `session_start` ('\xDE\x85\xCA\x90') to the event characteristic
* Create a `token` (see "Generate token" below)
* Write the result of `encrypt(mixA(mac_address, product_id), token)` to the token characteristic
* Should receive some data ('confirmation') in a notify from the token characreristic
* `token` should be equal to the result of `encrypt(mixB(mac_address, product_id), encrypt(mixA(mac_address, product_id), confirmation))`, if it's the case, continue, else, return an error
* `session_end` = '\xFA\x54\xAB\x92'
* Send the result of `encrypt(token, session_end)` to the token characteristic to confirm the registration

## Generate token

* That's how they do it in mi home: `token = md5_12('token.{}.{}'format(currentTimeMillis(), randFloat()))`
* I guess it could be anything really, as long as it's 12 bytes

## Crypt functions

Xiaomi for some reason (security by obscurity?) uses a native (in a JNI) implementation of RC4 and two custom functions that generate a "key" based on the mac address and the product ID.
You can check out [drndos's kettler PoC](https://github.com/drndos/mi-kettle-poc/blob/master/mi-kettle.py) which is based on [aprosvetova's reverse engineering of the JNI](https://github.com/aprosvetova/xiaomi-kettle), which also contains an implementation of the RC4 of `blecipher.so` (the JNI used in mi home)
You can find python implementations of the `mixA`, `mixB` and `encrypt` functions of the JNI below.

### MixA

``` python
def mixA(mac, productid):
  return bytes([mac[0], mac[2], mac[5], (productid & 0xff), (productid & 0xff), mac[4], mac[5], mac[1]])
```

### MixB

``` python
def mixB(mac, productid):
  return bytes([mac[0], mac[2], mac[5], ((productid >> 8) & 0xff), mac[4], mac[0], mac[5], (productid & 0xff)])
```

### Encrypt

``` python
def encrypt(key, data):
    # KSA
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA
    j = 0
    keystream = []
    for i in range(len(data)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        keystream.append(S[(S[i] + S[j]) % 256])

    # Encrypt
    return bytes(a ^ b for a, b in zip(data, keystream))
```

## Conclusion & Thanks

It's a bit surprising to find such a "complex" (compared to what's the devices are doing) system for authentication, but it's actually a nice surprise to find that xiaomi didn't forgot the security on their devices. Sadly, some OEMs doesn't completly respect this security, and some devices can be accessed for some time without authentication, you'll get disconnected after a timeout eventually.
There should be everything here to init and connect to some devices, without being kicked out after some time.
Thanks to `aprosvetova` for her amazing reverse engineering work on the JNI and `drndos` for the python port (didn't have to mess with crypto algorithms in python yay!).
Also thanks to `vkolotov` and some others i probably forgot for their initial work on the authentication mechanism.
Thanks to Mijia for being nice enough to give a SDK without any obfuscation like in mi home so it was much easier to reverse engineer this protocol.
