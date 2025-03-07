from cryptography.fernet import Fernet
import base64
import sys

def decrypt_file(input_path, output_path):
    # 使用固定密钥
    fixed_key = "あなた、ご自分の事ばかりですのね".encode('utf-8')
    # 确保密钥长度为32字节
    key = base64.urlsafe_b64encode(fixed_key[:32].ljust(32, b'\0'))
    
    f = Fernet(key)
    
    # 读取加密文件
    with open(input_path, 'rb') as file:
        encrypted_data = file.read()
    
    # 解密数据
    decrypted_data = f.decrypt(encrypted_data)
    
    # 保存解密后的文件
    with open(output_path, 'wb') as file:
        file.write(decrypted_data)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python decrypt_tool.py <加密文件路径> <输出文件路径>")
        print("例如: python decrypt_tool.py ./static/resources/test_encrypted.bin decrypted_test.txt")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        decrypt_file(input_file, output_file)
        print(f"解密成功！解密后的文件已保存为: {output_file}")
    except Exception as e:
        print(f"解密失败: {str(e)}") 