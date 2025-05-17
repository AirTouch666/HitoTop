# HitoTop 打包指南

本指南将帮助你将 HitoTop 一言应用打包成 macOS 可执行的 `.app` 应用程序。

## 使用 PyInstaller

### 环境准备

1. 确保已安装 Python 3.6 或更高版本：

   ```bash
   python3 --version
   ```

2. 安装所需的依赖包：

   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### 使用打包脚本

我们提供了一个专门的打包脚本，可以自动完成所有步骤：

```bash
python build_with_pyinstaller.py
```

脚本会自动：
1. 清理之前的构建文件
2. 创建必要的 .spec 文件
3. 运行 PyInstaller 构建应用
4. 在成功时提示应用程序位置

### 手动打包

如果想手动控制打包过程，可以直接使用 PyInstaller：

```bash
# 基本打包命令
pyinstaller --name="HitoTop" --windowed --clean --noconfirm hitotop.py

# 或者使用更详细的配置
pyinstaller --name="HitoTop" --windowed --clean --noconfirm \
  --hidden-import=rumps --hidden-import=objc --hidden-import=Foundation \
  --hidden-import=AppKit --hidden-import=PyObjCTools \
  hitotop.py
```

## 应用程序使用

无论使用哪种打包方法，最终的 `.app` 文件都可以直接双击运行或拖到 Applications 文件夹中。应用程序会在屏幕顶部显示一言，并在系统状态栏提供控制菜单。

## 签名和公证（可选）

如果想分发应用给其他用户，可能需要进行签名和公证：

```bash
# 签名应用
codesign --force --deep --sign "Developer ID Application: Your Name" ./dist/HitoTop.app

# 创建公证包
ditto -c -k --keepParent ./dist/HitoTop.app ./HitoTop.zip

# 提交公证
xcrun altool --notarize-app --primary-bundle-id "com.yourname.hitotop" --username "your@apple.id" --password "@keychain:AC_PASSWORD" --file HitoTop.zip

# 添加公证票据
xcrun stapler staple ./dist/HitoTop.app
```

希望这些信息能帮助你成功打包 HitoTop 应用程序！ 