[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java
version = 0.1
requirements = python3,kivy,requests
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE
android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2