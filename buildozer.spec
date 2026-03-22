[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.2
requirements = python3,kivy,requests
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,FOREGROUND_SERVICE,RECEIVE_BOOT_COMPLETED,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.add_src = FlowScriptService.java
android.add_res = res
android.manifest.services = FlowScriptService
android.add_manifests = manifest_patch.xml
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2