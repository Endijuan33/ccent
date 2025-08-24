[app]
title = Central Jati Cell
package.name = centraljaticell
package.domain = com.central
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pyzbar,pillow,openssl,sqlite3,android
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

# Permissions
android.permissions = CAMERA,INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android build config
android.api = 33
android.minapi = 21
android.ndk = 25b
p4a.branch = master
android.gradle_dependencies = com.journeyapps:zxing-android-embedded:4.3.0
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
