#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HitoTop 打包脚本 - 使用 PyInstaller 打包
"""

import os
import sys
import subprocess
import shutil
import plistlib

# 创建 .spec 文件内容
SPEC_CONTENT = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['hitotop.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['rumps', 'objc', 'Foundation', 'AppKit', 'PyObjCTools', 'certifi', 'urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HitoTop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HitoTop',
)

app = BUNDLE(
    coll,
    name='HitoTop.app',
    icon=None,
    bundle_identifier='com.yourname.hitotop',
    info_plist={
        'LSUIElement': True,
        'CFBundleName': 'HitoTop',
        'CFBundleDisplayName': 'HitoTop',
        'CFBundleIdentifier': 'com.yourname.hitotop',
        'CFBundleVersion': '0.1.0',
        'CFBundleShortVersionString': '0.1.0',
        'NSHighResolutionCapable': True,
    },
)
'''

def clean_previous_build():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    if os.path.exists('hitotop.spec'):
        os.remove('hitotop.spec')

def create_spec_file():
    """创建 PyInstaller 规格文件"""
    print("创建 .spec 文件...")
    with open('hitotop.spec', 'w') as f:
        f.write(SPEC_CONTENT)

def build_app():
    """运行 PyInstaller 构建应用"""
    print("正在构建应用程序...")
    cmd = ['pyinstaller', 'hitotop.spec', '--clean']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    print(stdout.decode('utf-8'))
    
    if process.returncode != 0:
        print("构建失败！错误信息:")
        print(stderr.decode('utf-8'))
        return False
    
    return True

def main():
    """主函数"""
    print("===== 开始打包 HitoTop 应用 =====")
    
    clean_previous_build()
    create_spec_file()
    
    if build_app():
        print("\n===== 打包成功! =====")
        print("应用程序位置: dist/HitoTop.app")
        print("你可以将它拖到应用程序文件夹中，或直接运行它")
    else:
        print("\n===== 打包失败! =====")
        print("请检查错误信息并解决问题")

if __name__ == "__main__":
    main() 