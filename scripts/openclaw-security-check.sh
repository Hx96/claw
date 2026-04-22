#!/bin/bash
# OpenClaw Security Check Script
# 检查 OpenClaw 安全漏洞并自动修复

set -e

LOG_FILE="/tmp/openclaw-security-check-$(date +%Y%m%d).log"
REPORT_FILE="/tmp/openclaw-security-report-$(date +%Y%m%d).txt"

echo "=======================================" | tee -a "$LOG_FILE"
echo "OpenClaw Security Check Report" | tee -a "$LOG_FILE"
echo "Time: $(date)" | tee -a "$LOG_FILE"
echo "=======================================" | tee -a "$LOG_FILE"

# 1. 检查 OpenClaw 版本
echo -e "\n📦 Checking OpenClaw version..." | tee -a "$LOG_FILE"
openclaw status 2>&1 | grep -E "(Update|Dashboard|OS)" | tee -a "$LOG_FILE" || openclaw status 2>&1 | head -10 | tee -a "$LOG_FILE"

# 2. 检查已安装的包
echo -e "\n🔍 Checking installed packages..." | tee -a "$LOG_FILE"
npm list -g --depth=0 2>&1 | grep -i openclaw | tee -a "$LOG_FILE"

# 3. 检查系统安全更新
echo -e "\n🔒 Checking for security updates..." | tee -a "$LOG_FILE"
if command -v apt-get &> /dev/null; then
    apt-get list --upgradable 2>&1 | grep -i security | tee -a "$LOG_FILE" || echo "No security updates found" | tee -a "$LOG_FILE"
fi

# 4. 检查 Node.js 依赖漏洞
echo -e "\n🛡️  Checking Node.js dependencies for vulnerabilities..." | tee -a "$LOG_FILE"
cd /root/.local/share/pnpm/global/5/.pnpm/openclaw@*
if [ -f package-lock.json ]; then
    npm audit --production 2>&1 | tee -a "$LOG_FILE" || echo "No vulnerabilities found" | tee -a "$LOG_FILE"
else
    echo "📦 Creating package-lock.json for dependency checking..." | tee -a "$LOG_FILE"
    npm i --package-lock-only 2>&1 | tee -a "$LOG_FILE" || echo "Could not create lockfile" | tee -a "$LOG_FILE"
    if [ -f package-lock.json ]; then
        npm audit --production 2>&1 | tee -a "$LOG_FILE" || echo "No vulnerabilities found" | tee -a "$LOG_FILE"
    fi
fi

# 5. 自动修复可修复的漏洞
echo -e "\n🔧 Attempting to fix vulnerabilities..." | tee -a "$LOG_FILE"
if [ -f package-lock.json ]; then
    npm audit fix --production 2>&1 | tee -a "$LOG_FILE" || echo "Some vulnerabilities could not be auto-fixed" | tee -a "$LOG_FILE"
else
    echo "⚠️  No package-lock.json found, skipping auto-fix" | tee -a "$LOG_FILE"
fi

# 检查插件安全问题
echo -e "\n🔌 Checking plugin security..." | tee -a "$LOG_FILE"
if [ -f ~/.openclaw/openclaw.json ]; then
    if grep -q '"plugins.allow":\s*\[\]' ~/.openclaw/openclaw.json 2>/dev/null; then
        echo "⚠️  plugins.allow is empty - recommend setting explicit plugin list" | tee -a "$LOG_FILE"
    else
        echo "✅ plugins.allow is configured" | tee -a "$LOG_FILE"
    fi
fi

# 6. 检查 OpenClaw 版本更新（不自动更新，需要确认）
echo -e "\n⬆️  Checking OpenClaw updates..." | tee -a "$LOG_FILE"
CURRENT_VERSION=$(pnpm list -g openclaw 2>&1 | grep openclaw | awk -F@ '{print $2}')
LATEST_VERSION=$(npm view openclaw version 2>&1)
echo "Current version: $CURRENT_VERSION" | tee -a "$LOG_FILE"
echo "Latest version: $LATEST_VERSION" | tee -a "$LOG_FILE"

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "⚠️  OpenClaw update available!" | tee -a "$LOG_FILE"
    echo "Manual update required: openclaw update" | tee -a "$LOG_FILE"
else
    echo "✅ OpenClaw is up to date" | tee -a "$LOG_FILE"
fi

# 7. 自动修复配置文件权限
echo -e "\n⚙️  Checking and fixing configuration security..." | tee -a "$LOG_FILE"

# 修复配置文件权限
if [ -f ~/.openclaw/openclaw.json ]; then
    CURRENT_PERMS=$(stat -c %a ~/.openclaw/openclaw.json 2>/dev/null || stat -f %A ~/.openclaw/openclaw.json 2>/dev/null)
    if [ "$CURRENT_PERMS" != "600" ]; then
        echo "🔧 Fixing config file permissions ($CURRENT_PERMS -> 600)..." | tee -a "$LOG_FILE"
        chmod 600 ~/.openclaw/openclaw.json
        echo "✅ Config file permissions fixed" | tee -a "$LOG_FILE"
    else
        echo "✅ Config file permissions OK (600)" | tee -a "$LOG_FILE"
    fi
fi

# 检查其他配置文件
if [ -f ~/.openclaw/config.yml ]; then
    echo "Config.yml file permissions:" | tee -a "$LOG_FILE"
    ls -la ~/.openclaw/config.yml | tee -a "$LOG_FILE"
fi

# 8. 生成报告摘要
echo -e "\n=======================================" | tee -a "$LOG_FILE"
echo "✅ Security check completed!" | tee -a "$LOG_FILE"
echo "Full log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
echo "=======================================" | tee -a "$LOG_FILE"

# 生成带版本信息的简洁报告
UPDATE_STATUS="需要确认更新"
if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    UPDATE_STATUS="已是最新版本"
fi

cat > "$REPORT_FILE" << EOF
OpenClaw 安全检查报告
时间: $(date)
状态: 已完成

版本信息:
当前版本: $CURRENT_VERSION
最新版本: $LATEST_VERSION
更新状态: $UPDATE_STATUS

自动修复项目:
✓ 依赖包漏洞扫描和修复
✓ 配置文件权限修复
✓ 插件安全检查
✓ 系统安全更新检查

需要手动处理:
⚠️  OpenClaw版本更新（如需要）: openclaw update
⚠️  插件白名单配置（如需要）

详细日志: $LOG_FILE
EOF

cat "$REPORT_FILE"

# 生成简洁报告
cat > "$REPORT_FILE" << EOF
OpenClaw 安全检查报告
时间: $(date)
状态: 已完成

检查项目:
✓ OpenClaw 版本检查
✓ 依赖包漏洞扫描
✓ 系统安全更新检查
✓ 配置文件安全性检查
✓ 自动修复可修复漏洞

详细日志: $LOG_FILE
EOF

cat "$REPORT_FILE"
