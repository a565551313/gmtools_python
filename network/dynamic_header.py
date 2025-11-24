#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态包头计算器
根据MessagePack数据长度动态计算正确的PACKET_HEADER
"""

def calculate_packet_header(msgpack_length):
    """
    根据MessagePack数据长度计算4字节包头

    Args:
        msgpack_length: MessagePack打包后的数据长度

    Returns:
        bytes: 4字节的包头
    """
    # 后两个字节固定（从Lua源码观察得出）
    last_two_bytes = b"\x80\xcb"

    # 当长度超过512字节时需要进位
    if msgpack_length > 512:
        # 每768字节为一段
        # 768-1023: first_byte=0x00-0xff, second_byte=3
        # 1024-1279: first_byte=0x00-0x7f, second_byte=4 (在256后继续)
        # 当第一字节达到0xff时，第二字节+1
        
        # 计算在768后的长度（从0开始）
        offset_from_768 = msgpack_length - 768
        
        # 每256字节第一字节重新开始，第二字节+1
        segment = offset_from_768 // 256
        first_byte = offset_from_768 % 256
        
        # 第二字节从3开始
        second_byte = 3 + segment
    else:
        # 线性关系：first_byte = 0x80 + (length - 384)
        # 长度每增加1，第一字节增加1
        first_byte = (0x80 + (msgpack_length - 384)) & 0xFF
        second_byte = 0x01

    # 组装包头
    header = bytes([first_byte, second_byte]) + last_two_bytes

    return header


def get_packet_header_for_data(packed_data):
    """
    为实际的MessagePack数据计算包头

    Args:
        packed_data: MessagePack打包后的数据（bytes）

    Returns:
        bytes: 4字节的包头
    """
    return calculate_packet_header(len(packed_data))


# 测试
if __name__ == "__main__":
    test_cases = [
        # 长度 ≤ 512，不进位
        376,  # 已知案例
        384,  # 已知案例
        386,  # 用户提到
        360,  # 预测
        368,  # 预测
        372,  # 预测
        380,  # 预测
        388,  # 预测
        392,  # 预测
        396,  # 预测
        400,  # 预测
        512,  # 边界值：恰好512字节

        # 长度 > 512，进位机制
        513,  # 开始进位
        516,  # 用户验证案例
        520,  # 预测
        600,  # 预测
        800,  # 预测
        939,  # 用户测试案例
    ]

    print("Dynamic PACKET_HEADER Calculator")
    print("=" * 50)
    print("\n【长度 ≤ 512，不进位】")
    for length in test_cases:
        if length <= 512:
            header = calculate_packet_header(length)
            print(f"Length {length:3d} -> Header: {header.hex()}")

    print("\n【长度 > 512，进位机制】")
    for length in test_cases:
        if length > 512:
            header = calculate_packet_header(length)
            print(f"Length {length:3d} -> Header: {header.hex()}")
