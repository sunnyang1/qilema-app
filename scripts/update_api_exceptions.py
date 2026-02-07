"""
批量更新API文件中的HTTPException为自定义异常类
"""

import os
import re

# 定义需要更新的文件和对应的替换规则
FILES_TO_UPDATE = [
    {
        "file": "/Users/michelleye/CodeBuddy/qilema-app/app/api/emergency_centers.py",
        "imports": {
            "old": "from fastapi import APIRouter, Depends, HTTPException, status",
            "new": "from fastapi import APIRouter, Depends, status\nfrom app.core.exceptions import ValidationException, NotFoundException, ForbiddenException"
        },
        "replacements": [
            ("raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))", "raise ValidationException(detail=str(e))"),
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"呼叫记录不存在\")", "raise NotFoundException(\"呼叫记录不存在\")"),
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权限访问\")", "raise ForbiddenException(\"无权限访问\")"),
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权限操作\")", "raise ForbiddenException(\"无权限操作\")"),
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"救援记录不存在\")", "raise NotFoundException(\"救援记录不存在\")"),
        ]
    },
    {
        "file": "/Users/michelleye/CodeBuddy/qilema-app/app/api/emergency_resources.py",
        "imports": {
            "old": "from fastapi import APIRouter, Depends, HTTPException, status",
            "new": "from fastapi import APIRouter, Depends, status\nfrom app.core.exceptions import NotFoundException"
        },
        "replacements": [
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"资源不存在\")", "raise NotFoundException(\"资源不存在\")"),
        ]
    },
    {
        "file": "/Users/michelleye/CodeBuddy/qilema-app/app/api/notifications.py",
        "imports": {
            "old": "from fastapi import APIRouter, Depends, HTTPException, status",
            "new": "from fastapi import APIRouter, Depends, status\nfrom app.core.exceptions import ValidationException, NotFoundException, ForbiddenException"
        },
        "replacements": [
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权发送给其他用户\")", "raise ForbiddenException(\"无权发送给其他用户\")"),
            ("raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=\"发送通知失败\")", "raise ValidationException(\"发送通知失败\")"),
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权查看其他用户的通知\")", "raise ForbiddenException(\"无权查看其他用户的通知\")"),
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权标记其他用户的通知\")", "raise ForbiddenException(\"无权标记其他用户的通知\")"),
            ("raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=\"无权设置其他用户的偏好\")", "raise ForbiddenException(\"无权设置其他用户的偏好\")"),
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"通知偏好设置不存在\")", "raise NotFoundException(\"通知偏好设置不存在\")"),
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"通知模板不存在\")", "raise NotFoundException(\"通知模板不存在\")"),
        ]
    },
    {
        "file": "/Users/michelleye/CodeBuddy/qilema-app/app/api/sos_requests.py",
        "imports": {
            "old": "from fastapi import APIRouter, Depends, HTTPException, status",
            "new": "from fastapi import APIRouter, Depends, status\nfrom app.core.exceptions import ValidationException, NotFoundException"
        },
        "replacements": [
            ("raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=\"SOS记录不存在\")", "raise NotFoundException(\"SOS记录不存在\")"),
            ("raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=\"只能取消待处理的SOS求助\")", "raise ValidationException(\"只能取消待处理的SOS求助\")"),
        ]
    },
]


def update_file(config):
    """更新单个文件"""
    file_path = config["file"]
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新导入语句
    if config["imports"]["old"] in content:
        content = content.replace(config["imports"]["old"], config["imports"]["new"])
        print(f"✅ 已更新导入语句: {file_path}")
    else:
        print(f"⚠️ 未找到导入语句: {file_path}")
    
    # 执行替换
    for old, new in config["replacements"]:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ 已替换: {old[:50]}...")
        else:
            print(f"  ⚠️ 未找到: {old[:50]}...")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 完成: {file_path}\n")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("批量更新API文件 - 替换HTTPException为自定义异常")
    print("=" * 60)
    print()
    
    success_count = 0
    for config in FILES_TO_UPDATE:
        if update_file(config):
            success_count += 1
    
    print("=" * 60)
    print(f"完成! 成功更新 {success_count}/{len(FILES_TO_UPDATE)} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    main()
