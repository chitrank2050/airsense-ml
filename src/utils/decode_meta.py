from email.header import decode_header


def decode_meta(value: str) -> str:
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8")
    return decoded
