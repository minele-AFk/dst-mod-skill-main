---
name: dst-audio-camera-effects
description: Manage Don't Starve Together audio, sound effects, music, and camera behavior. Use when adding sound cues, ambient audio, music transitions, camera zoom, and camera constraints.
---

# DST 音频与相机表现

先区分世界空间音效、个人 UI/音乐和本地相机。资源、发声端与取消路径分别确定。

## 音频合同

SoundEmitter 是 inst.entity:AddSoundEmitter() 建立的引擎对象，不是 AddComponent("soundemitter")。PlaySound 使用已加载工程的完整事件路径，不直接传 WAV/MP3。

Designer 管线为音频母版 → FDP → FEV 事件元数据及所需 FSB 银行 → Asset("SOUNDPACKAGE", ...) / Asset("SOUND", ...) → 事件调用。一份 FEV 可依赖多个 FSB；不要固定成一事件一对文件。其他音频管线先验证目标版本接入，不把 Studio .bank 与 FEV/FSB 混用。

循环声音使用本机制唯一句柄，重复进入不叠加，退出用同一句柄 KillSound。世界音效参照当前同类 Prefab/SG 的发声端与复制行为；个人音乐由本地生命周期管理。不能一概要求只在服务器或只在客机播放，更不能用 not ismastersim 漏掉房主的可视客户端。

原版 dynamicmusic 使用 TheFocalPoint.SoundEmitter 等路径；不以未核实的 TheAudio/CrossFade 当通用背景音乐 API。RemapSoundEvent 会影响对应原事件的使用者，局部角色效果先考虑独立事件。

## 相机合同

先读 cameras/followcamera.lua 与当前调用者。该快照可见 SetDistance、SetMinDistance、SetMaxDistance、ZoomIn、ZoomOut、SetTarget、Shake；各签名与时机逐项核对，不猜 Zoom() 或全局 SetCameraConstraint()。

临时瞄准、过场和震屏只管理本地相机；退出、死亡、重连或控制目标改变时恢复自己接管的字段。恢复前核对当前拥有者，避免旧效果结束时覆盖后来进入的相机模式。

## 验证与资源

音频验收包括事件首次触发、连续触发、循环停止、近远距离、混音滑块和换世界。无声专服只证明脚本路径，不能证明银行解码或听感。相机检查取消、不同窗口比例、目标失效与其他模式接管。

- [FMOD 打包与替换](references/fmod-sound-packaging.md)。
- [音频与粒子补充](../../engineering/dst-mod-engineering/audio-particles.md)：资源依赖、空间设置、工具与证据边界。
- [前端管理](../../systems/thefrontend.md)。
- 本轮源码入口：components/dynamicmusic.lua、cameras/followcamera.lua；[快照记录](../../core/dst-source-research/references/source-research.md#2026-10-17-知识内容复核)。
