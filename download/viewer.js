let currentFilePath = null;
let currentFileType = null;

// 初始化事件监听器
document.addEventListener('DOMContentLoaded', function() {
    // 为所有打开按钮添加事件监听器
    document.querySelectorAll('.open-btn').forEach(button => {
        button.addEventListener('click', function() {
            const fileItem = this.parentElement;
            openFile(fileItem);
        });
    });

    // 解密按钮
    document.getElementById('decrypt-btn').addEventListener('click', decryptFile);

    // 取消按钮
    document.getElementById('cancel-btn').addEventListener('click', cancelDecrypt);

    // 关闭按钮
    document.getElementById('close-btn').addEventListener('click', closeContent);

    // 密码输入框回车事件
    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            decryptFile();
        }
    });
});

function openFile(fileItem) {
    currentFilePath = fileItem.dataset.path;
    currentFileType = fileItem.dataset.type;
    
    if (currentFileType === 'encrypted') {
        // 显示密码输入框
        document.getElementById('password-form').style.display = 'block';
        document.getElementById('error-message').style.display = 'none';
        document.getElementById('password').value = '';
        document.getElementById('password').focus();
    } else if (currentFileType === 'image') {
        // 直接显示图片
        showContent(`<img src="${currentFilePath}" style="max-width: 100%;">`);
    }
}

async function decryptFile() {
    try {
        const password = document.getElementById('password').value;
        if (!password) {
            showError('请输入密码');
            return;
        }

        // 获取加密文件
        const response = await fetch(currentFilePath);
        const encryptedData = await response.arrayBuffer();
        
        // 首先提取文件扩展名（前16字节）
        const extBytes = new Uint8Array(encryptedData.slice(0, 16));
        const decoder = new TextDecoder();
        const ext = decoder.decode(extBytes).trim().replace(/\0/g, '');
        
        // 获取实际的加密数据
        const actualEncryptedData = encryptedData.slice(16);
        
        // 准备32字节密钥
        const encoder = new TextEncoder();
        const keyBytes = encoder.encode(password).slice(0, 32);
        const paddedKey = new Uint8Array(32);
        paddedKey.set(keyBytes);  // 自动补0到32字节
        
        // 准备16字节IV（全零）
        const iv = new Uint8Array(16);
        
        // 导入密钥
        const key = await window.crypto.subtle.importKey(
            'raw',
            paddedKey.buffer,
            { name: 'AES-CBC', length: 256 },
            false,
            ['decrypt']
        );
        
        // 解密
        const decrypted = await window.crypto.subtle.decrypt(
            {
                name: 'AES-CBC',
                iv: iv
            },
            key,
            actualEncryptedData
        );

        // 移除PKCS7填充
        const decryptedArray = new Uint8Array(decrypted);
        const paddingLength = decryptedArray[decryptedArray.length - 1];
        const unpaddedData = decryptedArray.slice(0, -paddingLength);
        
        // 创建blob并设置正确的文件名
        const blob = new Blob([unpaddedData]);
        const url = URL.createObjectURL(blob);
        
        // 从文件路径中提取基本文件名，并添加原始扩展名
        const baseName = currentFilePath.split('/').pop().replace('.bin', '');
        const fileName = baseName + ext;
        
        showContent(`
            <div style="text-align: center; padding: 20px;">
                <p>文件已解密</p>
                <a href="${url}" download="${fileName}" 
                   class="download-btn" 
                   style="display: inline-block; 
                          padding: 10px 20px; 
                          background: #4CAF50; 
                          color: white; 
                          text-decoration: none; 
                          border-radius: 4px;">
                    下载文件
                </a>
            </div>
        `);

        // 隐藏密码输入框
        document.getElementById('password-form').style.display = 'none';
        document.getElementById('error-message').style.display = 'none';
    } catch (error) {
        console.error('解密失败:', error);
        showError('密码错误或文件损坏');
    }
}

function showContent(html) {
    const contentBody = document.getElementById('content-body');
    contentBody.innerHTML = html;
    document.getElementById('content').style.display = 'block';
}

function closeContent() {
    const content = document.getElementById('content-body');
    // 找到所有的 blob URL 并释放
    const blobUrls = content.querySelectorAll('a[href^="blob:"]');
    blobUrls.forEach(element => {
        URL.revokeObjectURL(element.href);
    });
    
    document.getElementById('content').style.display = 'none';
    content.innerHTML = '';
}

function cancelDecrypt() {
    document.getElementById('password-form').style.display = 'none';
    document.getElementById('error-message').style.display = 'none';
    currentFilePath = null;
    currentFileType = null;
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
} 