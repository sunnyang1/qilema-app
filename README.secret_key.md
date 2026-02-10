# SECRET_KEY 配置说明

## 为什么需要SECRET_KEY？

SECRET_KEY用于签名JWT令牌，保护API安全。如果SECRET_KEY泄露，攻击者可以伪造令牌，访问用户账户。

## 如何生成安全的SECRET_KEY？

使用项目提供的脚本生成强随机密钥：

```bash
# 从项目根目录
python backend/scripts/generate_secret_key.py

# 或从backend目录
cd backend
python scripts/generate_secret_key.py
```

输出示例：
```
生成的SECRET_KEY:
1pmR_AnoDS8OS8Jl_eSks-F1hVagG6xz8ki5KVm58bS_MZqvnHTfzL6MOf6taoHhx_IAKmdFAxg45QkWKWjFdg==

密钥长度: 88 字节

请在.env文件中设置:
SECRET_KEY=1pmR_AnoDS8OS8Jl_eSks-F1hVagG6xz8ki5KVm58bS_MZqvnHTfzL6MOf6taoHhx_IAKmdFAxg45QkWKWjFdg==
```

## 配置步骤

1. 复制`.env.example`为`.env`：
   ```bash
   cp .env.example .env
   ```

2. 生成SECRET_KEY：
   ```bash
   python backend/scripts/generate_secret_key.py
   ```

3. 将生成的SECRET_KEY复制到`.env`文件：
   ```
   SECRET_KEY=<生成的密钥>
   ```

4. 重启应用使配置生效

## 安全注意事项

### ✅ 必须做的

- ✅ 使用至少64字节的强随机密钥
- ✅ 不要在代码中硬编码SECRET_KEY
- ✅ 不要将`.env`文件提交到版本控制
- ✅ 生产环境使用唯一的SECRET_KEY
- ✅ 定期更换SECRET_KEY（建议每3-6个月）

### ❌ 绝对禁止

- ❌ 使用默认值`your-secret-key-change-in-production`
- ❌ 使用简单密码如`123456`、`password`
- ❌ 将SECRET_KEY提交到Git
- ❌ 在公开场合分享SECRET_KEY
- ❌ 在多个环境使用相同的SECRET_KEY

## 验证配置是否正确

应用启动时会自动验证SECRET_KEY：

- ❌ 使用默认值 → 抛出错误，应用无法启动
- ❌ 密钥太短（<64字节）→ 抛出错误，应用无法启动
- ❌ 生产环境密钥强度不足 → 抛出错误，应用无法启动
- ✅ 配置正确 → 应用正常启动

## 密钥强度要求

### 开发/测试环境
- 最小长度：64字节
- 字符类型：无特殊要求

### 生产环境
- 最小长度：64字节
- 字符类型：至少包含3种（大写、小写、数字、特殊字符）

脚本生成的密钥自动满足所有要求。

## 如果忘记SECRET_KEY

如果忘记SECRET_KEY，需要：

1. 生成新的SECRET_KEY
2. 更新`.env`文件
3. 重启应用

**注意**：更换SECRET_KEY后，所有现有的JWT令牌将失效，用户需要重新登录。

## 疑难解答

### Q: 应用启动报错"SECRET_KEY不能使用默认值"
**A**: 按照上述步骤生成新的SECRET_KEY并配置。

### Q: 应用启动报错"SECRET_KEY长度至少64字节"
**A**: 使用`python backend/scripts/generate_secret_key.py`生成符合要求的密钥。

### Q: 更换SECRET_KEY后用户无法登录
**A**: 这是正常的，JWT令牌已失效。用户需要重新登录获取新令牌。

### Q: 可以在不同环境使用相同的SECRET_KEY吗？
**A**: 不推荐。每个环境应该使用独立的SECRET_KEY以降低风险。
