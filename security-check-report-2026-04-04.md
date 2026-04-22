# OpenClaw Daily Security Check Report
**Date:** April 4, 2026, 10:30 PM Asia/Shanghai  
**Status:** Completed with multiple critical issues requiring attention

## Summary
- **Critical Issues:** 6
- **Warnings:** 6  
- **Info Items:** 1
- **Vulnerabilities found in plugins:** 19 total across 6 plugins

## Critical Issues Found

### 1. Plugin Code Safety Issues (19 findings)
- **adp-openclaw**: 3 critical issues (credential harvesting, shell execution)
- **openclaw-plugin-yuanbao**: 1 critical issue (shell execution)
- **openclaw-qqbot**: 10 critical issues (multiple credential harvesting, shell execution)
- **openclaw-weixin**: 1 critical issue (credential harvesting)
- **wecom**: 3 critical issues (shell execution, credential harvesting)
- **follow-builders skill**: 2 critical issues (credential harvesting)

### 2. Missing File Permissions
- Fixed 7 session files with chmod 600
- Missing permissions on credentials and auth-profiles directories

## Warnings Addressed

### 1. Security Configuration
- **Reverse proxy trust**: Missing trusted proxies config
- **Plugin allowlist**: Not set (7 extensions present)
- **Tool policy**: Permissive policy allows plugin tools
- **NPM specs**: Unpinned dependencies found
- **Integrity metadata**: Missing for lightclawbot plugin

### 2. Attack Surface
- Tools elevated: enabled
- Webhooks: disabled
- Internal hooks: enabled
- Browser control: enabled

## Actions Taken

### ✅ Completed
1. Fixed file permissions for session files
2. Audited dependencies (0 vulnerabilities found)
3. Confirmed no outdated packages

### ⚠️ Requires Attention
1. **Review plugin source code** - All flagged plugins contain potentially dangerous patterns
2. **Configure trusted proxies** - Add reverse proxy IPs if exposing Control UI
3. **Set plugin allowlist** - Restrict to trusted plugin IDs only
4. **Pin dependency versions** - Update to exact version specs
5. **Update plugin metadata** - Refresh integrity hashes for lightclawbot

## Recommendations

### High Priority
1. **Review or remove suspicious plugins**: Consider removing plugins with credential harvesting concerns
2. **Restrict tool policies**: Use minimal/coding profiles instead of default permissive policy
3. **Configure security hardening**: Set proper allowlists and trusted proxies

### Medium Priority  
1. **Update dependencies**: Pin all npm specs to exact versions
2. **Refresh plugin metadata**: Reinstall lightclawbot for integrity hashes

### Low Priority
1. **Monitor attack surface**: Current configuration shows personal assistant trust model
2. **File permission maintenance**: Regular chmod checks recommended

## Next Steps
1. Review plugin source code for flagged issues
2. Configure security settings based on exposure requirements
3. Schedule regular plugin and dependency updates
4. Consider implementing allowlists for production use

---
*Check completed: April 4, 2026, 10:30 PM Asia/Shanghai*