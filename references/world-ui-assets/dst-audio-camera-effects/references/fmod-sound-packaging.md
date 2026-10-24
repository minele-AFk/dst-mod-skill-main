# FMOD 音效打包与替换

> 用 FMOD Designer 打包自定义音效，再通过 `RemapSoundEvent` 替换原版音效。出处以本地 `D:\mods\scripts` 源码与官方 samplesound 模板为准。

## 声明与替换（modmain.lua）

```lua
Assets = {
    Asset("SOUNDPACKAGE", "sound/soundexample.fev"), -- 事件
    Asset("SOUND", "sound/modsounds.fsb"),            -- 音频数据
}
RemapSoundEvent("dontstarve/creatures/bat/flap", "soundexample/creatures/bat/pop")
```

## 打包流程

1. 用 **FMOD Designer** 建工程（模板 `basic3dsound.fdt`，XML）。
2. 事件按 `eventgroup` 层级组织（如 `creatures > bat`），叶子是事件 `pop`（全名 `soundexample/creatures/bat/pop`），sounddef 引 wav 源文件；bank 名 `modsounds`。
3. 将实际需要的 soundexample.fev 及它依赖的全部 FSB 银行放入 Mod；本例只有 modsounds.fsb，不推广成所有工程固定两个文件。

## 关键点

- `RemapSoundEvent(原事件名, mod内事件全名)`：第一参游戏原事件；第二参不带 bank 名的 fdp 层级路径。
- `.fdt` 是 FMOD Designer 工程模板（3D 音效用 `basic3dsound`）。

## 循环、来源与验收

循环 PlaySound 的 handle 使用私有名；KillSound 使用同一 handle，提前取消也要清理。世界发声端按原版同类对象核对，个人音乐按本地玩家生命周期管理，避免房主/客机双播或漏播。3D 模式、距离曲线、游戏坐标尺度与混音分类分别验证。

原始音频与工程保留，输出到独立目录。银行存在、字符串中出现事件名或无声专服经过调用都不能证明可播放；最终检查真实客户端的首次播放、循环停止、近远距离和音量滑块。完整制作与工具边界见 [音频补充](../../../engineering/dst-mod-engineering/audio-particles.md)。
