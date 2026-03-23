#!/bin/bash
# WSL2 Gateway 自动恢复脚本
# 用途：检测 Gateway 状态，异常时自动重启

LOG_FILE="/tmp/openclaw/watchdog.log"
MAX_RESTARTS=3
RESTART_COUNT_FILE="/tmp/openclaw/restart_count"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查 Gateway 是否可访问
check_gateway() {
    curl -s --connect-timeout 3 http://127.0.0.1:18789/ > /dev/null 2>&1
    return $?
}

# 重启 Gateway
restart_gateway() {
    log "🔄 尝试重启 Gateway..."
    
    # 读取重启计数
    if [ -f "$RESTART_COUNT_FILE" ]; then
        count=$(cat "$RESTART_COUNT_FILE")
    else
        count=0
    fi
    
    # 防止无限重启
    if [ $count -ge $MAX_RESTARTS ]; then
        log "❌ 已达到最大重启次数 ($MAX_RESTARTS)，停止自动重启"
        return 1
    fi
    
    # 重启
    openclaw gateway restart
    sleep 3
    
    if check_gateway; then
        log "✅ Gateway 重启成功"
        echo $((count + 1)) > "$RESTART_COUNT_FILE"
        return 0
    else
        log "❌ Gateway 重启失败"
        echo $((count + 1)) > "$RESTART_COUNT_FILE"
        return 1
    fi
}

# 重置重启计数（当 Gateway 正常时调用）
reset_count() {
    echo "0" > "$RESTART_COUNT_FILE"
}

# 主逻辑
# 成功时静默（不输出），只在失败时记录日志
if check_gateway; then
    reset_count
    # 静默成功，不输出任何内容
    exit 0
else
    log "⚠️ Gateway 无响应，尝试重启..."
    restart_gateway
    if [ $? -eq 0 ]; then
        log "🔔 通知：Gateway 已自动恢复"
    else
        log "🚨 警告：Gateway 重启失败，请手动检查！"
    fi
    exit $?
fi
