"""
GMTools网络客户端模块
实现TCP连接、数据包发送接收、加密解密
"""

import socket
import threading
import time
import sys
import os
from typing import Optional, Callable, Dict, Any, Tuple

import msgpack

# Add project root to path before importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.encryptor import GMToolsEncryptor  # noqa: E402
from config.settings import (  # noqa: E402
    SERVER_HOST,
    SERVER_PORT,
    SEPARATOR,
)
from .dynamic_header import calculate_packet_header  # noqa: E402


class GMToolsClient:
    """GMTools TCP客户端"""

    def __init__(self):
        """初始化客户端"""
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.reconnect_interval = 3  # 重连间隔（秒）
        self.max_reconnect_attempts = 30
        self.reconnect_count = 0
        self._recv_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._is_closing = False  # 添加关闭标志
        self._socket_lock = threading.Lock()  # 保护socket访问的锁
        self._unpacker = msgpack.Unpacker(raw=False)  # 持久化unpacker，处理流式数据

        # 回调函数
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_receive: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

    def _initialize_socket(self):
        """初始化并连接socket"""
        with self._socket_lock:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.reconnect_count = 0

    def _cleanup_socket_on_error(self):
        """在错误时清理socket资源"""
        self.connected = False
        with self._socket_lock:
            if self.socket:
                try:
                    self.socket.close()
                except (OSError, AttributeError) as e:
                    logger.debug(f"Socket close error during connection failure: {e}")
                self.socket = None

    def connect(self, host: str = None, port: int = None) -> bool:
        """连接到服务器 - 重构后的简化版本

        Args:
            host: 服务器地址
            port: 服务器端口

        Returns:
            bool: 连接成功返回True,否则返回False
        """
        if host:
            self.host = host
        if port:
            self.port = port

        try:
            self._initialize_socket()
            self._start_receive_thread()

            if self.on_connect:
                self.on_connect()

            print(f"[[OK]] 连接服务器成功: {self.host}:{self.port}")
            return True

        except Exception as e:
            self._cleanup_socket_on_error()
            print(f"[[FAIL]] 连接服务器失败: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def disconnect(self):
        """断开连接"""
        self._stop_event.set()
        self.connected = False

        # 使用锁保护socket关闭操作
        with self._socket_lock:
            if self.socket:
                try:
                    self.socket.close()
                except (OSError, AttributeError) as e:
                    logger.debug(f"Socket close error during disconnect: {e}")
                self.socket = None

        # 如果正在关闭程序，不调用回调以避免访问已销毁的对象
        if not self._is_closing and self.on_disconnect:
            try:
                self.on_disconnect()
            except (RuntimeError, AttributeError) as e:
                # Ignore callback exceptions (e.g., RuntimeError for destroyed Qt objects)
                logger.debug(f"Disconnect callback error: {e}")

        print("[i] 已断开服务器连接")

    def _start_receive_thread(self):
        """启动接收线程"""
        if self._recv_thread and self._recv_thread.is_alive():
            return

        self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_thread.start()

    def _try_unpack_data(self, data: bytes, length: int) -> bool:
        """尝试解包指定长度的数据

        Args:
            data: 要解包的数据
            length: 要尝试的长度

        Returns:
            bool: 是否成功解包
        """
        try:
            temp_unpacker = msgpack.Unpacker(raw=False)
            temp_unpacker.feed(data[:length])
            next(iter(temp_unpacker))
            return True
        except (msgpack.OutOfData, StopIteration):
            return False
        except (msgpack.ExtraData, ValueError, TypeError) as e:
            logger.debug(f"MessagePack unpacking error at length {length}: {e}")
            return False

    def _handle_single_byte(self, data: bytes) -> int:
        """处理单字节数据

        Args:
            data: 单字节数据

        Returns:
            int: 消耗的字节数
        """
        try:
            temp_unpacker = msgpack.Unpacker(raw=False)
            temp_unpacker.feed(data)
            next(iter(temp_unpacker))
            return 1
        except (msgpack.OutOfData, StopIteration, msgpack.ExtraData):
            return 1

    def _binary_search_min_length(self, data: bytes) -> int:
        """使用二分查找找到最小可解包长度

        Args:
            data: 数据字节

        Returns:
            int: 最小可解包长度
        """
        low = 1
        high = len(data)
        result = len(data)  # 默认值

        while low <= high:
            mid = (low + high) // 2
            if self._try_unpack_data(data, mid):
                result = mid
                high = mid - 1
            else:
                low = mid + 1

        return result

    def _calculate_consumed_bytes(self, data: bytes) -> int:
        """计算MessagePack数据实际消耗的字节数 - 重构后的简化版本

        使用二分查找的方法找到能成功解包的最小字节数

        Args:
            data: MessagePack编码的字节数据

        Returns:
            int: 实际消耗的字节数
        """
        if not data:
            return 0

        if len(data) == 1:
            return self._handle_single_byte(data)

        return self._binary_search_min_length(data)

    def _receive_socket_data(self) -> Optional[bytes]:
        """
        从socket接收数据块

        Returns:
            接收到的数据块，如果连接断开则返回None
        """
        with self._socket_lock:
            if not self.socket:
                print("[DEBUG] Socket无效，退出接收循环")
                return None
            sock = self.socket

        # 在锁外进行接收操作
        chunk = sock.recv(4096)
        if not chunk:
            print("[!] 服务器断开连接")
            return None

        print(f"[DEBUG] 收到数据 {len(chunk)} 字节")
        return chunk

    def _process_packet(
        self, buffer: bytes, processed_bytes: int, iteration: int
    ) -> tuple[int, bool]:
        """
        处理单个数据包

        Args:
            buffer: 数据缓冲区
            processed_bytes: 已处理的字节数
            iteration: 当前迭代次数

        Returns:
            tuple[新的processed_bytes, 是否继续处理]
        """
        packet_start = processed_bytes
        packet_header = buffer[packet_start : packet_start + 4]
        print(
            f"[DEBUG] 第{iteration}个数据包 - 位置: {packet_start}, Buffer剩余: {len(buffer) - processed_bytes}"
        )

        # 获取数据部分
        data_start = packet_start + 4
        remaining_data = buffer[data_start:]
        print(f"[DEBUG] 数据部分长度: {len(remaining_data)} 字节")

        # 尝试解包并处理数据
        try:
            consumed_bytes = self._unpack_and_handle_message(remaining_data)
            packet_length = 4 + consumed_bytes
            new_processed_bytes = processed_bytes + packet_length
            print(
                f"[DEBUG] 数据包长度: {packet_length} (包头:4, 数据:{consumed_bytes})"
            )
            print(
                f"[DEBUG] 已处理总字节数: {new_processed_bytes}, Buffer剩余: {len(buffer) - new_processed_bytes}"
            )
            return new_processed_bytes, True

        except msgpack.OutOfData:
            # 数据不完整，等待更多数据
            print(
                f"[DEBUG] 数据不完整，buffer剩余: {len(buffer) - processed_bytes} 字节，退出处理循环"
            )
            return processed_bytes, False

        except StopIteration:
            # 没有更多对象可解包
            print("[DEBUG] 没有更多对象可解包，退出处理循环")
            return processed_bytes, False

        except Exception as e:
            # 解析或解密错误，跳过1字节再试
            print(f"[!] MessagePack解析错误: {e}")
            return processed_bytes + 1, True

    def _unpack_and_handle_message(self, data: bytes) -> int:
        """
        解包并处理消息数据

        Args:
            data: 要解包的数据

        Returns:
            消耗的字节数

        Raises:
            msgpack.OutOfData: 数据不完整
            StopIteration: 没有更多对象
        """
        # 创建临时unpacker处理当前数据包
        temp_unpacker = msgpack.Unpacker(raw=False)
        temp_unpacker.feed(data)

        # 尝试解包一个对象
        unpacked = next(iter(temp_unpacker))
        print("[DEBUG] 成功解包MessagePack数据")

        # 提取并解密数据
        if isinstance(unpacked, list) and len(unpacked) > 0:
            self._decrypt_and_dispatch(unpacked[0])

        # 计算消耗的字节数
        return self._calculate_consumed_bytes(data)

    def _decrypt_and_dispatch(self, encrypted_content: str):
        """
        解密并分发消息到UI

        Args:
            encrypted_content: 加密的内容
        """
        # 解密字符串
        decrypted_str = GMToolsEncryptor.decrypt(encrypted_content)
        print(f"[+] 收到并解密的数据: {decrypted_str}")

        # 解析序号和内容
        seq_no, content = self._parse_response(decrypted_str)
        if seq_no is not None:
            print(f"[+] 序号: {seq_no}, 内容: {content}")

            # 传递给UI处理
            if self.on_receive:
                self.on_receive(
                    {"seq_no": seq_no, "content": content, "raw_data": decrypted_str}
                )

    def _process_buffer(self, buffer: bytes) -> tuple[bytes, int]:
        """
        处理缓冲区中的所有完整数据包

        Args:
            buffer: 数据缓冲区

        Returns:
            tuple[更新后的buffer, 已处理的字节数]
        """
        processed_bytes = 0
        iteration = 0

        # 循环处理缓冲区中的所有数据包
        while len(buffer) - processed_bytes >= 4:
            iteration += 1
            new_processed, should_continue = self._process_packet(
                buffer, processed_bytes, iteration
            )
            processed_bytes = new_processed

            if not should_continue:
                break

        # 移除已处理的数据
        if processed_bytes > 0:
            old_len = len(buffer)
            buffer = buffer[processed_bytes:]
            print(
                f"[DEBUG] 清理Buffer: {old_len} -> {len(buffer)} 字节，移除了 {processed_bytes} 字节"
            )
        else:
            print(f"[DEBUG] 未处理任何数据，Buffer长度: {len(buffer)}")

        return buffer, processed_bytes

    def _handle_os_error(self, error: OSError) -> bool:
        """处理OSError类型的错误

        Args:
            error: OSError异常

        Returns:
            是否应该断开连接
        """
        if hasattr(error, "winerror") and error.winerror == 10038:
            # "在一个非套接字上尝试了一个操作"
            print("[!] Socket已无效，退出接收循环")
            return True
        else:
            print(f"[!] 网络错误: {error}")
            if self.on_error:
                self.on_error(error)
            return True

    def _handle_receive_error(self, error: Exception) -> bool:
        """处理接收数据时的错误 - 重构后的简化版本

        Args:
            error: 发生的异常

        Returns:
            是否应该断开连接
        """
        if isinstance(error, socket.timeout):
            # 超时是正常的，继续等待
            return False

        elif isinstance(error, (ConnectionAbortedError, ConnectionResetError)):
            # 连接被对方重置或中止
            print(f"[!] 连接异常断开: {error}")
            return True

        elif isinstance(error, OSError):
            return self._handle_os_error(error)

        else:
            # 其他异常，记录但不断开连接
            print(f"[!] 接收数据异常: {error}")
            if self.on_error:
                self.on_error(error)
            return False

    def _should_continue_receiving(self) -> bool:
        """检查是否应该继续接收数据"""
        return not self._stop_event.is_set() and self.connected

    def _process_incoming_chunk(self, buffer: bytes) -> Tuple[bytes, bool]:
        """处理传入的数据块

        Args:
            buffer: 当前缓冲区数据

        Returns:
            tuple: (新缓冲区, 是否应该停止接收)
        """
        chunk = self._receive_socket_data()
        if chunk is None:
            return buffer, True

        buffer += chunk
        print(f"[DEBUG] Buffer总长度: {len(buffer)} 字节")

        new_buffer, _ = self._process_buffer(buffer)
        return new_buffer, False

    def _cleanup_connection(self):
        """清理连接状态"""
        self.connected = False
        if self.on_disconnect:
            self.on_disconnect()

    def _receive_loop(self):
        """接收数据循环 - 重构后的简化版本"""
        buffer = b""
        print("[DEBUG] 接收循环启动")

        while self._should_continue_receiving():
            try:
                buffer, should_stop = self._process_incoming_chunk(buffer)
                if should_stop:
                    break

            except Exception as e:
                if self._handle_receive_error(e):
                    break

        self._cleanup_connection()

    def _recv_exact(self, length: int) -> Optional[bytes]:
        """
        精确接收指定长度的数据

        Args:
            length: 需要接收的字节数

        Returns:
            接收到的数据,失败返回None
        """
        data = b""
        while len(data) < length:
            chunk = self.socket.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def _extract_seq_no(self, response: str) -> Optional[tuple[int, int]]:
        """
        提取序号和内容起始位置

        Returns:
            Optional[tuple]: (序号, 内容字段起始位置) 或 None
        """
        import re

        seq_match = re.search(r"序号\s*=\s*(\d+)", response)
        if not seq_match:
            print("[!] 未找到序号字段")
            return None

        seq_no = int(seq_match.group(1))
        print(f"[DEBUG] 找到序号: {seq_no}")

        # 从序号后面开始查找 "内容="
        content_key_start = seq_match.end()
        content_key_match = re.search(r"内容\s*=\s*", response[content_key_start:])
        if not content_key_match:
            print("[!] 未找到内容字段")
            return None

        value_start = content_key_start + content_key_match.end()
        return seq_no, value_start

    def _parse_string_content(self, response: str, value_start: int) -> Optional[str]:
        """解析字符串格式的内容"""
        quote_end = response.find('"', value_start + 1)
        if quote_end == -1:
            print("[!] 未找到字符串结束引号")
            return None

        content = response[value_start + 1 : quote_end]
        print(f"[DEBUG] 找到字符串内容，长度: {len(content)}")
        return content

    def _parse_dict_content(self, response: str, value_start: int) -> Optional[str]:
        """解析字典格式的内容"""
        print("[DEBUG] 开始解析字典格式...")
        brace_count = 0
        content_end = value_start

        for i in range(value_start, len(response)):
            if response[i] == "{":
                brace_count += 1
            elif response[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    content_end = i + 1
                    break

        if brace_count > 0:
            print("[!] 未找到字典结束大括号")
            return None

        content = response[value_start:content_end]
        print(f"[DEBUG] 找到字典内容，长度: {len(content)}")
        return content

    def _parse_response(self, response: str) -> tuple[Optional[int], Optional[str]]:
        """
        解析服务器返回的数据 - 重构后的简化版本

        Args:
            response: 格式如: do local ret={序号=7,内容="#Y/登录成功"} return ret end

        Returns:
            tuple: (序号, 内容)，解析失败返回(None, None)
        """
        try:
            # 提取序号和内容起始位置
            result = self._extract_seq_no(response)
            if not result:
                return None, None

            seq_no, value_start = result

            # 根据内容格式解析
            value_char = response[value_start]
            if value_char == '"':
                content = self._parse_string_content(response, value_start)
            elif value_char == "{":
                content = self._parse_dict_content(response, value_start)
            else:
                print(f"[!] 内容字段格式未知: {value_char}")
                return None, None

            if content is None:
                return None, None

            return seq_no, content

        except Exception as e:
            print(f"[!] 解析响应异常: {e}")
            import traceback

            traceback.print_exc()
            return None, None

    def _validate_packet_header(self, data: bytes) -> bool:
        """验证数据包标头

        Args:
            data: 原始数据

        Returns:
            bool: 标头是否有效
        """
        # 包头格式: 0x?? 0x?? 0x80 0xCB
        # 当长度 ≤ 512 时：0x?? 0x01 0x80 0xCB
        # 当长度 > 512 时：0x?? 0x02 0x80 0xCB
        if len(data) >= 4 and data[2:4] != b"\x80\xcb":
            print(f"[!] 数据标头不匹配1: {data.hex()}")
            return False
        return True

    def _process_decrypted_data(self, decrypted_str: str):
        """处理解密后的数据

        Args:
            decrypted_str: 解密后的字符串
        """
        seq_no, content = self._parse_response(decrypted_str)
        if seq_no is not None:
            if self.on_receive:
                self.on_receive(
                    {
                        "seq_no": seq_no,
                        "content": content,
                        "raw_data": decrypted_str,
                    }
                )
        print(f"[i] 收到服务器响应: {decrypted_str[:100]}...")

    def _handle_received_data(self, data: bytes):
        """处理接收到的数据 - 重构后的简化版本

        Args:
            data: 原始数据（包含标头）
        """
        try:
            # 验证标头
            if not self._validate_packet_header(data):
                return

            # 去掉标头
            packed_data = data[4:]

            # MessagePack解码
            unpacked = msgpack.unpackb(packed_data, raw=False)

            # 提取数据内容
            if isinstance(unpacked, list) and len(unpacked) > 0:
                encrypted_content = unpacked[0]

                # 解密
                decrypted_str = GMToolsEncryptor.decrypt(encrypted_content)

                # 处理解密数据
                self._process_decrypted_data(decrypted_str)

        except Exception as e:
            print(f"[!] 处理接收数据失败: {e}")
            if self.on_error:
                self.on_error(e)

    def _format_data_string(self, seq_no: int, content: str, account: str) -> str:
        """格式化数据字符串

        Args:
            seq_no: 序号
            content: 内容
            account: 账号

        Returns:
            str: 格式化后的数据字符串
        """
        if seq_no == 1:
            # 登录格式：序号 + 分隔符 + 内容 + 分隔符
            return f"{seq_no}{SEPARATOR}{content}{SEPARATOR}"
        else:
            # 其他功能格式：序号 + 分隔符 + 内容 + 分隔符 + 账号
            return f"{seq_no}{SEPARATOR}{content}{SEPARATOR}{account}"

    def _log_data_info(
        self,
        seq_no: int,
        data: str,
        encrypted_data: str,
        packed: bytes,
        final_data: bytes,
    ):
        """记录数据发送信息"""
        print(f"【Python】原始数据: {data}")
        print(f"【Python】原始数据长度: {len(data)} 字节")
        print(f"【Python】序号: {seq_no}, 是否添加账号后缀: {seq_no != 1}")
        print(f"【Python】加密后数据: {encrypted_data}")
        print(f"【Python】加密后数据长度: {len(encrypted_data)} 字节")
        print(f"[Python] MessagePack打包后数据: {packed}")
        print(f"[Python] MessagePack打包后数据长度: {len(packed)} 字节")
        hex_str = " ".join([f"{b:02x}" for b in packed])
        print(f"[Python] MessagePack打包后数据(十六进制): {hex_str}")
        print(f"[Python] MessagePack打包后数据(十六进制)长度: {len(packed)} 字节")
        print(f"[Python] 添加标头后数据: {final_data}")
        print(f"[Python] 最终发送数据长度: {len(final_data)} 字节")

    def _prepare_packet(self, seq_no: int, content: str, account: str) -> bytes:
        """准备要发送的数据包

        Args:
            seq_no: 序号
            content: 内容
            account: 账号

        Returns:
            bytes: 最终的数据包
        """
        # 格式化数据字符串
        data = self._format_data_string(seq_no, content, account)

        # 加密
        encrypted_data = GMToolsEncryptor.encrypt(data)

        # 使用MessagePack打包
        packed = msgpack.packb([encrypted_data], use_bin_type=True)

        # 动态计算包头
        packet_header = calculate_packet_header(len(packed))

        # 添加标头
        final_data = packet_header + packed

        # 记录调试信息
        self._log_data_info(seq_no, data, encrypted_data, packed, final_data)

        return final_data

    def _send_packet(self, final_data: bytes, seq_no: int) -> bool:
        """通过socket发送数据包

        Args:
            final_data: 要发送的数据
            seq_no: 序号

        Returns:
            bool: 发送是否成功
        """
        with self._socket_lock:
            if not self.socket:
                print("[!] 未连接到服务器")
                return False
            self.socket.sendall(final_data)
            print(f"[Python] 数据发送成功 (序号: {seq_no})")
            return True

    def send(self, seq_no: int, content: Dict[str, Any], account: str) -> bool:
        """发送数据到服务器 - 重构后的简化版本

        Args:
            seq_no: 序号（登录为1）
            content: 发送的内容
            account: 账号

        Returns:
            bool: 发送成功返回True,否则返回False
        """
        if not self.connected:
            print("[!] 未连接到服务器")
            return False

        try:
            final_data = self._prepare_packet(seq_no, content, account)
            return self._send_packet(final_data, seq_no)

        except Exception as e:
            print(f"[!] 发送数据失败: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def send_login(self, account: str, password: str, seq_no: int = 1) -> bool:
        """
        发送登录数据包

        Args:
            account: 账号
            password: 密码
            seq_no: 序号,默认1

        Returns:
            bool: 发送成功返回True,否则返回False
        """
        # 登录数据格式：Lua代码字符串（不含账号字段）
        # 根据分析.txt: do local ret={["密码"]="123456",["账号"]="a123456"} return ret end
        login_data = f'do local ret={{["密码"]="{password}",["账号"]="{account}"}} return ret end'
        return self.send(seq_no, login_data, account)

    def reconnect(self):
        """尝试重连"""
        if self.connected:
            return

        if self.reconnect_count >= self.max_reconnect_attempts:
            print(f"[!] 达到最大重连次数 ({self.max_reconnect_attempts})")
            return

        self.reconnect_count += 1
        print(f"[i] 第 {self.reconnect_count} 次重连,{self.reconnect_interval}秒后...")
        time.sleep(self.reconnect_interval)

        if not self.connected:
            self.connect()

    def __del__(self):
        """析构函数"""
        # 标记为正在关闭，避免调用回调函数访问已销毁的对象
        self._is_closing = True
        try:
            self.disconnect()
        except (RuntimeError, OSError, AttributeError) as e:
            # Ignore all exceptions during cleanup (e.g., destroyed objects)
            logger.debug(f"Exception during __del__ cleanup: {e}")
