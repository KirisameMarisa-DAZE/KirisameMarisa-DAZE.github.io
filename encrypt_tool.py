from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from hashlib import sha256
import os

def encrypt_file(input_path, output_path, password):
    """使用AES-CBC加密文件，并在加密数据中嵌入原始文件名"""
    # 使用固定密钥
    key = password.encode('utf-8')[:32].ljust(32, b'\0')
    iv = b'\0' * 16  # 使用固定的全零IV
    
    # 获取原始文件名
    original_filename = os.path.basename(input_path)
    filename_bytes = original_filename.encode('utf-8')
    if len(filename_bytes) > 65535:
        raise ValueError("文件名过长（最大支持65535字节）")
    
    # 用2个字节存储文件名长度
    filename_len = len(filename_bytes).to_bytes(2, 'big')
    
    # 读取文件内容
    with open(input_path, 'rb') as f:
        file_data = f.read()
    if input_path.endswith('.txt'):
        # 确保文本内容被正确处理为二进制
        file_data = file_data.decode('utf-8').encode('utf-8')
    
    # 在构建数据包之前添加调试信息
    print(f"[调试] 文件名长度: {len(filename_bytes)} 字节")
    print(f"[调试] 文件名: {original_filename}")
    print(f"[调试] 文件内容长度: {len(file_data)} 字节")
    
    # 构建完整数据包：文件名长度 + 文件名 + 文件内容
    full_data = filename_len + filename_bytes + file_data
    
    print(f"[调试] 完整数据包长度: {len(full_data)} 字节")
    print(f"[调试] 文件名长度字节: {filename_len.hex()}")
    print(f"[调试] 数据包前32字节: {full_data[:32].hex()}")
    
    # 使用PKCS7填充（确保16字节对齐）
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(full_data) + padder.finalize()
    
    # 创建加密器
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # 加密数据
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存加密文件
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)

    # 验证填充结果（调试用）
    print(f"[调试] 原始数据长度: {len(full_data)}")
    print(f"[调试] 填充后长度: {len(padded_data)}")
    print(f"[调试] 填充字节: {padded_data[-16:]}")
    print(f"[调试] 填充前最后16字节: {full_data[-16:].hex()}")
    print(f"[调试] 填充后最后16字节: {padded_data[-16:].hex()}")

    # ===== 新增：计算加密后文件哈希 =====
    encrypted_hash = sha256(encrypted_data).hexdigest()
    
    # 存储哈希值到独立文件
    hash_dir = os.path.join(os.path.dirname(output_path), "hash")
    os.makedirs(hash_dir, exist_ok=True)
    hash_filename = os.path.basename(output_path) + ".hash"
    hash_path = os.path.join(hash_dir, hash_filename)
    
    with open(hash_path, 'w') as f:
        f.write(f"SHA256|{encrypted_hash}")

    # 调试输出
    print(f"[哈希] 加密文件哈希: {encrypted_hash}")

if __name__ == "__main__":
    # 使用固定密钥
    PASSWORD = "あなた、ご自分の事ばかりですのね"
    
    # 创建一个测试文本文件
    test_content = "测试"
    with open("test.txt", "w", encoding='utf-8') as f:
        f.write(test_content)
    
    # 加密测试文件
    encrypt_file("test.txt", "./static/resources/encrypted_001.bin", PASSWORD)
    print("测试文件加密完成")
    
    # 加密PDF文件
    encrypt_file("../../pdf.pdf", "./static/resources/encrypted_002.bin", PASSWORD)
    print("PDF文件加密完成")