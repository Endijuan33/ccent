[app]
title = Central Jati Cell
package.name = centraljaticell
package.domain = com.central.jati
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json
version = 1.0
requirements = 
    python3,
    kivy==2.1.0,
    kivymd==1.1.1,
    pillow,
    openssl,
    sqlite3,
    android,
    pyjnius,
    audiostream,
    requests,
    certifi

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

# Android specific
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.sdk = 33
android.gradle_dependencies = 
    'com.journeyapps:zxing-android-embedded:4.3.0'
android.archs = arm64-v8a, armeabi-v7a
android.permissions = 
    CAMERA,
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    WAKE_LOCK

# Buildozer settings
[buildozer]
log_level = 2
warn_on_root = 1
