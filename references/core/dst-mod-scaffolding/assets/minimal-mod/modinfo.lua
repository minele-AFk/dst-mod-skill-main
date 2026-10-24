name = "My DST Mod"
description = "Minimal DST mod skeleton."
author = "Your name"
version = "0.1.0"
api_version = 10
dst_compatible = true

-- 这里按新增双方内容起步。纯客户端或服务器逻辑项目需按实际依赖调整。
client_only_mod = false
all_clients_require_mod = true

configuration_options = {
    {
        name = "enabled",
        label = "Enabled",
        options = {
            { description = "Yes", data = true },
            { description = "No", data = false },
        },
        default = true,
    },
}

-- modicon 使用真实 XML/Element；透明来自 alpha，不按白色阈值删除主体。
-- 资源声明、图集、动画完整性按实际用途核对，不统一强制“三件套”。
