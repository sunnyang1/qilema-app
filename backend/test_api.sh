#!/bin/bash

# 后端 API 测试脚本
# 用于测试所有后端接口，验证功能是否正常

set -e  # 遇到错误立即退出

BASE_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +%s)
PHONE="1380013${TIMESTAMP}"

echo "=========================================="
echo "后端 API 测试脚本"
echo "=========================================="
echo "测试时间: $(date)"
echo "BASE_URL: $BASE_URL"
echo ""

# ========== 步骤 1: 检查服务健康状态 ==========
echo "========== 步骤 1: 检查服务健康状态 =========="
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" $BASE_URL/../health 2>&1 || echo "FAILED")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 服务健康检查通过"
    echo "响应: $RESPONSE_BODY"
else
    echo "❌ 服务健康检查失败 (HTTP $HTTP_CODE)"
    echo "响应: $RESPONSE_BODY"
    exit 1
fi

echo ""

# ========== 步骤 2: 注册用户 ==========
echo "========== 步骤 2: 注册用户 =========="
echo "注册手机号: $PHONE"

REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"$PHONE\",\"password\":\"Test123456\",\"name\":\"测试用户$TIMESTAMP\"}" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ 用户注册成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  用户注册返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 3: 登录获取 token ==========
echo "========== 步骤 3: 登录获取 token =========="
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$PHONE&password=Test123456" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 登录成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"

    # 提取 token
    TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null || echo "")

    if [ -n "$TOKEN" ]; then
        echo "Token: ${TOKEN:0:20}..."
    else
        echo "❌ 无法提取 token"
        exit 1
    fi
else
    echo "❌ 登录失败 (HTTP $HTTP_CODE)"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    exit 1
fi

echo ""

# ========== 步骤 4: 获取当前用户信息 ==========
echo "========== 步骤 4: 获取当前用户信息 =========="
ME_RESPONSE=$(curl -s $BASE_URL/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$ME_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$ME_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取用户信息成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "❌ 获取用户信息失败 (HTTP $HTTP_CODE)"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 5: 创建签到 ==========
echo "========== 步骤 5: 创建签到 =========="
CHECKIN_RESPONSE=$(curl -s -X POST $BASE_URL/checkins \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$CHECKIN_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$CHECKIN_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ 创建签到成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  创建签到返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 6: 获取签到记录 ==========
echo "========== 步骤 6: 获取签到记录 =========="
GET_CHECKINS_RESPONSE=$(curl -s $BASE_URL/checkins \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$GET_CHECKINS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$GET_CHECKINS_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取签到记录成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "❌ 获取签到记录失败 (HTTP $HTTP_CODE)"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 7: 获取设备列表 ==========
echo "========== 步骤 7: 获取设备列表 =========="
DEVICES_RESPONSE=$(curl -s $BASE_URL/devices \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$DEVICES_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$DEVICES_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取设备列表成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  获取设备列表返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 8: 获取健康档案 ==========
echo "========== 步骤 8: 获取健康档案 =========="
HEALTH_RESPONSE=$(curl -s $BASE_URL/health-records/1 \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取健康档案成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  获取健康档案返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 9: 获取紧急联系人 ==========
echo "========== 步骤 9: 获取紧急联系人 =========="
CONTACTS_RESPONSE=$(curl -s $BASE_URL/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$CONTACTS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$CONTACTS_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取紧急联系人成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  获取紧急联系人返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 10: 创建 SOS 求助 ==========
echo "========== 步骤 10: 创建 SOS 求助 =========="
SOS_RESPONSE=$(curl -s -X POST $BASE_URL/sos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"latitude":39.9042,"longitude":116.4074,"location":"北京市朝阳区"}' \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$SOS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$SOS_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo "✅ 创建 SOS 求助成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  创建 SOS 求助返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 11: 获取急救知识 ==========
echo "========== 步骤 11: 获取急救知识 =========="
KNOWLEDGE_RESPONSE=$(curl -s "$BASE_URL/knowledge?limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$KNOWLEDGE_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$KNOWLEDGE_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取急救知识成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  获取急救知识返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 步骤 12: 获取用药提醒 ==========
echo "========== 步骤 12: 获取用药提醒 =========="
MEDICATIONS_RESPONSE=$(curl -s $BASE_URL/medications \
  -H "Authorization: Bearer $TOKEN" \
  -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$MEDICATIONS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE_BODY=$(echo "$MEDICATIONS_RESPONSE" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 获取用药提醒成功"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo "⚠️  获取用药提醒返回 HTTP $HTTP_CODE"
    echo "响应: $RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
fi

echo ""

# ========== 测试完成 ==========
echo "=========================================="
echo "✅ 所有测试步骤已完成"
echo "=========================================="
echo ""
echo "总结："
echo "- 如有 ❌ 标记，请检查日志: tail -50 /tmp/backend.log"
echo "- 如有 ⚠️ 标记，可能是正常情况（空数据等）"
echo "- 如有 RecursionError，请检查 ORM 对象序列化"
echo ""
