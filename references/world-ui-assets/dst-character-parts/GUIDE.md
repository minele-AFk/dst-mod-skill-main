---
name: dst-character-parts
description: 将人物立绘、三视图或已有角色图拆分为《饥荒联机版》Spriter/SCML人物动画可用的透明PNG部件，并保持画风、比例、方向、遮挡层级、画布、pivot和文件命名一致。用于制作或更新DST人物Mod美术，尤其是用户要求“人物拆件”“角色拆分”“把三视图做成动画部件”“替换人物Build贴图”“按SCML模板出零件”或检查拆件完整性时。
---

# DST 人物拆件

> 第三方参考边界：下文 Mod 分析笔记仅在用户明确要求参考对应 Mod 或这些笔记时读取；普通开发不主动打开或引用。详见 [共用约定](../../development-contract.md)。

把角色设定图转换为可装配、可转动、可编译的DST人物部件。优先复用目标人物的SCML结构，不把设定图简单切成互相粘连的矩形。

## 输出目标

交付以下内容：

- 与目标SCML相同路径、尺寸和命名的透明PNG部件。
- 一份从SCML生成的部件计划JSON。
- 一张拆件预览图和一份完整性检查报告。
- 必要时提供正面、背面、侧面重组预览；不要未经验证直接覆盖正式Build。

## 工作流程

### 0. 先判定：改已有人物 还是 从零新建

先判断本任务是"改造/替换一个已有角色的拆件"，还是"完全新建一个 DST 人物"：

- **已有目标 SCML（用户指定或最近可编译工程）** → 以目标 SCML 为准（模板优先级见 [dst-parts-spec.md](references/dst-parts-spec.md)）。
- **从零新建人物、或需要官方硬标准（部位/尺寸/pivot/资产清单）** → 先读取 [official-esctemplate-spec.md](references/official-esctemplate-spec.md)，按 20 部位官方帧数与 pivot 起步。

两者结论不冲突：官方 esctemplate 标准只用于"没有目标 SCML"时的起点；一旦拿到目标 SCML，立即切换到目标 SCML 优先。

### 1. 检查输入

1. 使用 `view_image` 以原始清晰度查看每张立绘或三视图。
2. 查找目标人物的 `exported/<character>/<character>.scml`。若已有SCML，必须以它的folder、file、尺寸和pivot为准。
3. 若没有SCML，先询问或选择最接近的官方/既有人物骨架作为模板，并明确这项假设；从零新建可参考 [official-esctemplate-spec.md](references/official-esctemplate-spec.md) 的官方部位规范表。
4. 保留原图，不在唯一原件上修改；新内容写入独立工作目录。

输入只有一个方向且其他方向不可可靠推断时，先制作方向设定图并让用户确认，再拆件。不要把正面五官直接旋转成侧脸。

### 2. 生成部件计划

运行：

```powershell
python tools/scml_parts_plan.py <角色.scml> --output <parts_plan.json>
```

读取生成的JSON，按实际folder逐项制作。不要凭通用清单删减目标SCML已有部件。
若条目含有 `source_image_error` 或 `source_path_case_mismatch`，先修复对应的损坏、不可读或大小写不一致源PNG；这些字段表示计划已保留SCML结构，但未能提取可选的源图Alpha元数据。计划、报告和预览使用各自的 `.json`/`.png` 输出路径；不要把预览写进部件根目录。

需要判断头发、裙摆、披风、蝴蝶结或饰品如何分层时，读取 [references/dst-parts-spec.md](references/dst-parts-spec.md)。

### 3. 锁定角色设计

重绘画风先读 [参考驱动提示流程](../dst-texture-style/references/reference-led-prompts.md)。人物主参考需能支持比例、面部、服装和方向；武器/物品例图只补充指定线条或材质，不能作为整个人物的画风与结构模板。部件检查使用实际装配尺寸，不统一缩成 64 图标。

在拆件前固定以下内容：

- 头身比、头部宽高、身体总高和脚底线。
- 正面、背面、侧面的发型轮廓与饰品所在一侧。
- 服装的袖口、腰线、裙长、鞋高和左右不对称细节。
- 描边粗细、阴影方向、颜色和纹理密度。

若这些内容在不同视图间冲突，先做一张修正版三视图，不要让不同零件分别“自行理解”角色设计。

### 4. 逐件拆分

对具有语义或被遮挡区域的零件，使用图像编辑/生成能力逐件处理；先看原图，再以原图作为编辑参考。一次只处理一个部件族，例如头部、头发、躯干或一条手臂。

遵守以下规则：

- 输出透明背景PNG，不带白底、棋盘格、环境阴影或其他身体部位。
- 保留原画风和原颜色，不擅自美化五官、改服装或改变头身比。
- 在关节和遮挡边缘补全必要的隐藏区域，使骨骼转动时不会露洞；补全区域延伸到可见接缝之外约部件长度的10%～15%。
- 头发至少按模板区分前发、后发及帽子遮挡版本；长发不要和躯干、手臂或裙子烘焙在一起。
- 上臂、下臂、手掌分别独立；沿袖口或关节的自然结构拆分。
- 裙摆、上衣和腿部保持独立；长裙按模板需要拆出前层、后层或左右摆片。
- 不把眼睛、嘴、腮红等表情烘焙进头部，除非目标SCML本来就是这种结构。
- 侧面通常由游戏镜像生成另一侧；角色存在明显左右不对称设计时，记录镜像会造成的错误，并准备独立素材或运行时覆盖方案。

### 5. 对齐画布与pivot

替换既有部件时：

1. 保持目标PNG的像素尺寸不变。
2. 保持SCML中的 `pivot_x/pivot_y` 不变。
3. 让关节锚点落在原模板相同位置，而不是把图像视觉居中。
4. 需要放大或缩小时围绕关节锚点变换，不围绕画布中心变换。
5. 保留透明留白；不要为了节省空间紧裁导致pivot漂移。

新增部件时，先确定pivot和父骨骼，再写入SCML。不要靠反复修改动画关键帧弥补错误的部件原点。

### 6. 重组验证

至少检查：

- 中立站立的正面、背面和侧面轮廓。
- `idle`、`run`、`attack`、`item_out/item_in`、受击和死亡动作。
- 戴帽子后的头发遮挡。
- 手持物品时双手与 `swap_object` 的层级。
- 长发、裙摆和手臂交叉时是否穿帮。
- 游戏镜像后的饰品方向。

先生成静态重组预览，再编译动画。发现比例或接缝错误时回到源部件修正，不在编译产物上累计变换。

### 7. 自动检查

运行：

```powershell
python tools/audit_parts.py <parts目录> --plan <parts_plan.json> --report <audit.json> --contact-sheet <contact_sheet.png> --strict
```

处理所有错误：缺图、路径大小写不一致、损坏或不可读图片、尺寸不符、非模板占位帧的空Alpha、无透明通道。DST素材路径必须与SCML中的大小写完全一致。目标模板原本就是全透明的占位帧只记为警告；边缘触碰和重复图片也属于警告，结合模板判断是否合理。

### 8. 交付与覆盖规则

- 明确列出已完成、尚待人工确认和无法从原图可靠恢复的部件。
- 只有重组预览和检查均通过后，才替换目标 `exported/<character>` 中的对应PNG。
- 编译前备份SCML和人物源工程；不要直接修改唯一的 `anim/<character>.zip`。
- 若用户要求正式更新，再调用项目自己的编译脚本生成Build，并按该项目交接说明同步游戏目录或发布包。

## 质量底线

不得交付以下结果：

- 只是把整个人物矩形裁成几块，部件仍带其他身体区域。
- 透明边缘带白边、黑边或棋盘纹。
- 三个方向的服装、发饰或身体比例互相矛盾。
- 手臂旋转后出现断口，长发与身体无法分层。
- 文件名看似正确，但像素尺寸或pivot与SCML不一致。
- 未经实测就声称动画Build已经可用。

## 按需参考

- 需要判断头发、裙摆、披风、蝴蝶结或饰品如何分层时读取 [dst-parts-spec.md](references/dst-parts-spec.md)（拆件规格）。
- 从零新建 DST 人物、需要官方硬标准（20 部位/尺寸/pivot/资产清单）时读取 [official-esctemplate-spec.md](references/official-esctemplate-spec.md)（官方标准）。
- 需要人物贴图强制尺寸（动画原图/saveslot/selectscreen/bigportrait/map_icons/avatars/names/modicon）时读取 [image-size-standards.md](references/image-size-standards.md)。
- 官方模板工程（SCML + 20 部位 PNG + anim zip + 硬标准图样）在 `../../../assets/dst-character-parts/official-template/`（skill 根 `assets/` 下，说明见 [README.md](../../../assets/dst-character-parts/official-template/README.md)）。
- 官方部位数据 `tools/esc_parts.json`；部位表导出 `tools/scml_analyze.py`（stdlib）；空白贴图模板/尺寸校验 `tools/char_sheet_gen.py`（Pillow，暂未验证运行，作标准理解底本）。
- 需要资产复用与动态加载（复用既有部件/Build 素材、运行时动态加载贴图、多语言模板、大 mod 目录骨架）时查阅 `references/mod-notes/` 下 [mod-mythwords.md](../../mod-notes/mod-mythwords.md)（神话书说原始笔记）。
