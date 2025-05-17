#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rumps
import requests
import threading
import time
import os
import AppKit
import objc
from PyObjCTools import AppHelper
import sys
import certifi
import ssl

class HitokotoApp:
    def __init__(self):
        self.window = None
        self.hitokoto_text = "加载中..."
        self.drag_start_pos = None
        self.setup_window()
        self.setup_menu()
        self.setup_right_click_menu()
        self.start_refresh_timer()
        self.update_text_color()
        
    def setup_window(self):
        # 获取屏幕尺寸
        screen_rect = AppKit.NSScreen.mainScreen().frame()
        window_width = 500
        window_height = 80
        
        # 将窗口放置在屏幕中央
        pos_x = (screen_rect.size.width - window_width) / 2
        pos_y = screen_rect.size.height - window_height - 60  # 放在屏幕顶部下方一点
        
        # 创建一个窗口
        self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(pos_x, pos_y, window_width, window_height),
            AppKit.NSWindowStyleMaskBorderless,
            AppKit.NSBackingStoreBuffered,
            False
        )
        
        # 设置窗口属性
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(AppKit.NSColor.clearColor())
        self.window.setLevel_(AppKit.NSStatusWindowLevel)
        self.window.setMovableByWindowBackground_(False)
        self.window.setAlphaValue_(1.0)
        
        # 创建主视图
        content_view = AppKit.NSView.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, window_width, window_height)
        )
        content_view.setWantsLayer_(True)
        
        # 设置视图为完全透明
        content_view.layer().setBackgroundColor_(AppKit.NSColor.clearColor().CGColor())
        
        # 设置圆角
        content_view.layer().setCornerRadius_(10.0)
        content_view.layer().setMasksToBounds_(True)
        
        self.window.setContentView_(content_view)
        
        # 创建文本字段 - 确保文字完全居中
        text_field = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(0, 0, window_width, window_height)  # 使用全部窗口空间
        )
        text_field.setEditable_(False)
        text_field.setSelectable_(True)
        text_field.setBezeled_(False)
        text_field.setDrawsBackground_(False)
        text_field.setAlignment_(AppKit.NSTextAlignmentCenter)
        text_field.setFont_(AppKit.NSFont.systemFontOfSize_(16))
        text_field.setStringValue_(self.hitokoto_text)
        text_field.setAlphaValue_(1.0)  
        
        # 设置文本字段的垂直居中
        text_field.setLineBreakMode_(AppKit.NSLineBreakByWordWrapping)
        text_field.setAlignment_(AppKit.NSTextAlignmentCenter)
        
        # 保存文本字段的引用
        self.text_field = text_field
        content_view.addSubview_(text_field)
        
        # 设置鼠标事件监听
        self.event_monitor = AppKit.NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
            AppKit.NSEventMaskLeftMouseDown | AppKit.NSEventMaskLeftMouseDragged | AppKit.NSEventMaskLeftMouseUp | AppKit.NSEventMaskRightMouseDown,
            self.handle_mouse_event
        )
        
        # 显示窗口
        self.window.makeKeyAndOrderFront_(None)
        
        # 注册系统外观变化通知
        notification_center = AppKit.NSDistributedNotificationCenter.defaultCenter()
        notification_center.addObserver_selector_name_object_(
            self,
            objc.selector(self.update_text_color, signature=b'v@:'),
            'AppleInterfaceThemeChangedNotification',
            None
        )
    
    def update_text_color(self):
        # 获取当前系统主题是否为暗色
        appearance = AppKit.NSAppearance.currentAppearance()
        if appearance is None:
            appearance = AppKit.NSApp.effectiveAppearance()
            
        # 从10.14开始，可以使用这个API判断
        if hasattr(appearance, 'name'):
            dark_mode = 'Dark' in appearance.name()
        else:
            # 对于旧版系统，尝试使用其他方法判断
            try:
                user_defaults = AppKit.NSUserDefaults.standardUserDefaults()
                dark_mode = user_defaults.stringForKey_('AppleInterfaceStyle') == 'Dark'
            except:
                # 默认使用白色
                dark_mode = True
        
        # 根据系统主题设置文字颜色
        if dark_mode:
            self.text_field.setTextColor_(AppKit.NSColor.whiteColor())
        else:
            self.text_field.setTextColor_(AppKit.NSColor.blackColor())
    
    def setup_menu(self):
        # 创建状态栏图标
        self.status_item = AppKit.NSStatusBar.systemStatusBar().statusItemWithLength_(AppKit.NSVariableStatusItemLength)
        self.status_item.setTitle_("言")
        
        # 创建菜单
        self.menu = AppKit.NSMenu.alloc().init()
        
        # 添加"刷新"菜单项
        refresh_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "刷新一言", "refresh:", ""
        )
        refresh_item.setTarget_(self)
        self.menu.addItem_(refresh_item)
        
        # 添加复制菜单项
        copy_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "复制一言", "copy_hitokoto:", ""
        )
        copy_item.setTarget_(self)
        self.menu.addItem_(copy_item)
        
        # 添加分隔线
        self.menu.addItem_(AppKit.NSMenuItem.separatorItem())
        
        # 添加"退出"菜单项
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "退出", "quit:", ""
        )
        quit_item.setTarget_(self)
        self.menu.addItem_(quit_item)
        
        # 设置菜单
        self.status_item.setMenu_(self.menu)
    
    def setup_right_click_menu(self):
        # 创建右键菜单
        self.right_click_menu = AppKit.NSMenu.alloc().init()
        
        # 添加"刷新"菜单项
        refresh_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "刷新一言", "refresh:", ""
        )
        refresh_item.setTarget_(self)
        self.right_click_menu.addItem_(refresh_item)
        
        # 添加"复制"菜单项
        copy_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "复制一言", "copy_hitokoto:", ""
        )
        copy_item.setTarget_(self)
        self.right_click_menu.addItem_(copy_item)
        
        # 添加分隔线
        self.right_click_menu.addItem_(AppKit.NSMenuItem.separatorItem())
        
        # 添加"退出"菜单项
        quit_item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "退出", "quit:", ""
        )
        quit_item.setTarget_(self)
        self.right_click_menu.addItem_(quit_item)
    
    def refresh_(self, sender):
        self.fetch_hitokoto()
    
    def copy_hitokoto_(self, sender):
        # 创建粘贴板对象
        pasteboard = AppKit.NSPasteboard.generalPasteboard()
        # 清除粘贴板
        pasteboard.clearContents()
        # 将一言文本复制到粘贴板
        pasteboard.setString_forType_(self.hitokoto_text, AppKit.NSPasteboardTypeString)
        print(f"已复制到剪贴板: {self.hitokoto_text}")
    
    def quit_(self, sender):
        AppKit.NSApp.terminate_(None)
        
    def handle_mouse_event(self, event):
        if event.type() == AppKit.NSEventTypeLeftMouseDown:
            # 检查是否按下了Command键
            if (event.modifierFlags() & AppKit.NSEventModifierFlagCommand):
                window_frame = self.window.frame()
                self.drag_start_pos = AppKit.NSEvent.mouseLocation()
                self.initial_window_origin = AppKit.NSPoint(window_frame.origin.x, window_frame.origin.y)
                return None  # 消费事件
                
        elif event.type() == AppKit.NSEventTypeLeftMouseDragged:
            if self.drag_start_pos and (event.modifierFlags() & AppKit.NSEventModifierFlagCommand):
                current_pos = AppKit.NSEvent.mouseLocation()
                delta_x = current_pos.x - self.drag_start_pos.x
                delta_y = current_pos.y - self.drag_start_pos.y
                
                new_origin = AppKit.NSPoint(
                    self.initial_window_origin.x + delta_x,
                    self.initial_window_origin.y + delta_y
                )
                
                self.window.setFrameOrigin_(new_origin)
                return None  # 消费事件
                
        elif event.type() == AppKit.NSEventTypeLeftMouseUp:
            self.drag_start_pos = None
        
        elif event.type() == AppKit.NSEventTypeRightMouseDown:
            # 在右键点击位置显示菜单
            event_location = event.locationInWindow()
            window_point = self.window.convertPointToScreen_(event_location)
            
            # 显示右键菜单
            AppKit.NSMenu.popUpContextMenu_withEvent_forView_(
                self.right_click_menu,
                event,
                self.window.contentView()
            )
            return None  # 消费事件
            
        return event  # 传递事件给下一个处理程序
    
    def fetch_hitokoto(self):
        try:
            # 使用certifi提供的CA证书路径以解决SSL验证问题
            if hasattr(ssl, '_create_unverified_context'):
                ssl_context = ssl._create_unverified_context()
            else:
                ssl_context = None

            # 尝试获取一言API
            response = requests.get(
                "https://v1.hitokoto.cn/", 
                timeout=10,
                verify=False  # 临时禁用SSL验证
            )
            
            if response.status_code == 200:
                data = response.json()
                hitokoto = data.get("hitokoto", "获取一言失败")
                source = data.get("from", "")
                
                if source:
                    self.hitokoto_text = f"{hitokoto} —— 《{source}》"
                else:
                    self.hitokoto_text = hitokoto
                    
                # 在主线程中更新UI
                AppKit.NSOperationQueue.mainQueue().addOperationWithBlock_(
                    lambda: self.text_field.setStringValue_(self.hitokoto_text)
                )
                
                print(f"获取到一言: {self.hitokoto_text}")
        except Exception as e:
            print(f"获取一言时出错: {e}")
            
            # 尝试使用备用API
            try:
                response = requests.get(
                    "https://api.apiopen.top/api/sentences", 
                    timeout=10,
                    verify=False
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        result = data.get("result", {})
                        hitokoto = result.get("name", "获取一言失败")
                        source = result.get("from", "")
                        
                        if source:
                            self.hitokoto_text = f"{hitokoto} —— 《{source}》"
                        else:
                            self.hitokoto_text = hitokoto
                        
                        # 在主线程中更新UI
                        AppKit.NSOperationQueue.mainQueue().addOperationWithBlock_(
                            lambda: self.text_field.setStringValue_(self.hitokoto_text)
                        )
                        print(f"从备用API获取到一言: {self.hitokoto_text}")
                        return
            except Exception as e2:
                print(f"备用API也失败: {e2}")
            
            self.hitokoto_text = "获取一言失败"
            AppKit.NSOperationQueue.mainQueue().addOperationWithBlock_(
                lambda: self.text_field.setStringValue_(self.hitokoto_text)
            )
    
    def start_refresh_timer(self):
        # 立即获取一次
        self.fetch_hitokoto()
        
        # 设置定时器，每小时获取一次
        def refresh_timer():
            while True:
                time.sleep(3600)  
                self.fetch_hitokoto()
        
        timer_thread = threading.Thread(target=refresh_timer, daemon=True)
        timer_thread.start()

def main():
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    app = HitokotoApp()
    AppKit.NSApplication.sharedApplication()
    AppHelper.runEventLoop()

if __name__ == "__main__":
    main() 