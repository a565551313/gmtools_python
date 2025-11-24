"""
GMTools加密解密模块
按照原始Lua代码的加密算法实现
"""

import base64


class GMToolsEncryptor:
    """GMTools加密解密工具类"""

    # 自定义字符替换表（来自Main.lua第29行）
    _BASE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/*=.，'

    # 加密映射表（来自Main.lua第30行）
    _ENCRYPT_MAP = {
        "B": "Cb,", "S": "3C,", "5": "6D,", "D": "2W,", "c": "dc,", "E": "cj,", "b": "vt,",
        "3": "Iv,", "s": "j1,", "N": "23,", "d": "mP,", "6": "wd,", "7": "7R,", "e": "ET,",
        "t": "nB,", "8": "9v,", "4": "yP,", "W": "j6,", "9": "Wa,", "H": "D2,", "G": "Ve,",
        "g": "JA,", "I": "Au,", "X": "NR,", "m": "DG,", "w": "Cx,", "Y": "Qi,", "V": "es,",
        "F": "pF,", "z": "CO,", "K": "XC,", "f": "aW,", "J": "DT,", "x": "S9,", "y": "xi,",
        "v": "My,", "L": "PW,", "u": "Aa,", "k": "Yx,", "M": "qL,", "j": "ab,", "r": "fN,",
        "q": "0W,", "T": "de,", "l": "P8,", "0": "q6,", "n": "Hu,", "O": "A2,", "1": "VP,",
        "i": "hY,", "h": "Uc,", "C": "cK,", "A": "f4,", "P": "is,", "U": "u2,", "o": "m9,",
        "Q": "vd,", "R": "gZ,", "2": "Zu,", "Z": "Pf,", "a": "Lq,", "p": "Sw,"
    }

    # 解密映射表（反向映射）
    _DECRYPT_MAP = {v: k for k, v in _ENCRYPT_MAP.items()}

    @classmethod
    def encode_base64(cls, data: str) -> str:
        """
        标准Base64编码
        对应Lua的encodeBase641函数
        注意：使用GBK编码以匹配LUA版本
        """
        encoded = base64.b64encode(data.encode('gbk')).decode('ascii')
        return encoded

    @classmethod
    def decode_base64(cls, data: str) -> str:
        """
        标准Base64解码
        对应Lua的decodeBase641函数
        注意：需要补充填充符'='
        注意：使用GBK解码以匹配LUA版本
        """
        # 补充Base64填充符
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return base64.b64decode(data).decode('gbk')

    @classmethod
    def encrypt(cls, data: str) -> str:
        """
        加密函数
        对应Lua的jm函数
        流程：标准Base64编码 + 自定义字符替换
        """
        # 第一步：标准Base64编码
        b64_data = cls.encode_base64(data)

        # 第二步：自定义字符替换
        encrypted = ""
        for char in b64_data:
            if char in cls._ENCRYPT_MAP:
                encrypted += cls._ENCRYPT_MAP[char]
            else:
                encrypted += char

        return encrypted

    @classmethod
    def decrypt(cls, data: str) -> str:
        """
        解密函数
        对应Lua的jm1函数
        流程：自定义字符替换还原 + 标准Base64解码
        """
        # 第一步：反向字符替换
        decrypted = data
        for encrypted_char, original_char in cls._DECRYPT_MAP.items():
            decrypted = decrypted.replace(encrypted_char, original_char)

        # 第二步：标准Base64解码
        return cls.decode_base64(decrypted)


def test_encryption():
    """测试加密解密功能"""
    test_data = "112345*-*12345hello12345*-*12345"

    encrypted = GMToolsEncryptor.encrypt(test_data)
    print(f"原始数据: {test_data}")
    print(f"加密后: {encrypted}")

    decrypted = GMToolsEncryptor.decrypt(encrypted)
    print(f"解密后: {decrypted}")

    assert test_data == decrypted, "加密解密测试失败!"
    print("[OK] 加密解密测试通过")


if __name__ == "__main__":
    test_encryption()
