# 用户管理系统 - 删除日志功能补丁

## 需要添加的功能

### 1. 后端 API（已完成）
- ✅ `DELETE /api/users/logs` - 删除指定日志
- ✅ `DELETE /api/users/logs/all` - 清空所有日志
- ✅ `AuditLog.delete_by_ids()` - 数据库删除方法
- ✅ `AuditLog.delete_all()` - 数据库清空方法
- ✅ `AuditLog.count_all()` - 统计日志数量

### 2. 前端 HTML 修改

在操作日志标签页（logsTab）中，需要修改表格结构：

```html
<!-- 在表格上方添加操作按钮 -->
<div style="margin-bottom: 15px; display: flex; gap: 10px; align-items: center;">
    <button class="btn btn-danger btn-small" onclick="deleteSelectedLogs()" id="deleteLogsBtn" disabled>
        删除选中
    </button>
    <button class="btn btn-warning btn-small" onclick="clearAllLogs()">
        清空所有日志
    </button>
    <span id="selectedLogsCount" style="color: #666; font-size: 14px;"></span>
</div>

<!-- 修改表头，添加复选框列 -->
<thead>
    <tr>
        <th style="width: 40px;">
            <input type="checkbox" id="selectAllLogs" onchange="toggleAllLogs(this.checked)">
        </th>
        <th>时间</th>
        <th>用户</th>
        <th>操作</th>
        <th>详情</th>
    </tr>
</thead>
```

### 3. 前端 JavaScript 函数

在 `<script>` 标签中添加以下函数：

```javascript
// 日志选择相关
let selectedLogIds = new Set();

// 全选/取消全选
function toggleAllLogs(checked) {
    const checkboxes = document.querySelectorAll('.log-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checked;
        if (checked) {
            selectedLogIds.add(parseInt(cb.value));
        } else {
            selectedLogIds.delete(parseInt(cb.value));
        }
    });
    updateDeleteButton();
}

// 单个日志选择
function toggleLogSelection(logId, checked) {
    if (checked) {
        selectedLogIds.add(logId);
    } else {
        selectedLogIds.delete(logId);
    }
    updateDeleteButton();
}

// 更新删除按钮状态
function updateDeleteButton() {
    const deleteBtn = document.getElementById('deleteLogsBtn');
    const countSpan = document.getElementById('selectedLogsCount');
    const count = selectedLogIds.size;
    
    deleteBtn.disabled = count === 0;
    countSpan.textContent = count > 0 ? `已选择 ${count} 条` : '';
    
    // 更新全选复选框状态
    const selectAll = document.getElementById('selectAllLogs');
    const checkboxes = document.querySelectorAll('.log-checkbox');
    if (selectAll && checkboxes.length > 0) {
        selectAll.checked = checkboxes.length === selectedLogIds.size;
    }
}

// 删除选中的日志
async function deleteSelectedLogs() {
    if (selectedLogIds.size === 0) return;
    
    if (!confirm(`确定要删除选中的 ${selectedLogIds.size} 条日志吗？`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/users/logs`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ log_ids: Array.from(selectedLogIds) })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message);
            selectedLogIds.clear();
            document.getElementById('selectAllLogs').checked = false;
            loadLogs();
        } else {
            alert(data.detail || '删除失败');
        }
    } catch (error) {
        alert(`删除失败: ${error.message}`);
    }
}

// 清空所有日志
async function clearAllLogs() {
    if (!confirm('⚠️ 警告：确定要清空所有操作日志吗？\n此操作不可恢复！')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/users/logs/all`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert(data.message);
            selectedLogIds.clear();
            document.getElementById('selectAllLogs').checked = false;
            loadLogs();
        } else {
            alert(data.detail || '清空失败');
        }
    } catch (error) {
        alert(`清空失败: ${error.message}`);
    }
}
```

### 4. 修改 loadLogs 函数

在现有的 `loadLogs` 函数中，修改渲染日志列表的部分，添加复选框：

```javascript
// 原来的代码
tbody.innerHTML = data.logs.map(log => `
    <tr>
        <td>${new Date(log.created_at).toLocaleString()}</td>
        <td>${log.username || 'N/A'}</td>
        <td>${log.action}</td>
        <td>${log.details || 'N/A'}</td>
    </tr>
`).join('');

// 修改为
tbody.innerHTML = data.logs.map(log => `
    <tr>
        <td>
            <input type="checkbox" class="log-checkbox" value="${log.id}" 
                   onchange="toggleLogSelection(${log.id}, this.checked)">
        </td>
        <td>${new Date(log.created_at).toLocaleString()}</td>
        <td>${log.username || 'N/A'}</td>
        <td>${log.action}</td>
        <td>${log.details || 'N/A'}</td>
    </tr>
`).join('');

// 重置选择状态
selectedLogIds.clear();
updateDeleteButton();
```

## 使用说明

1. 后端 API 已经全部实现完成
2. 需要手动修改 `static/user-management.html` 文件：
   - 在操作日志表格上方添加操作按钮
   - 在表头添加全选复选框
   - 在每行日志前添加复选框
   - 在 JavaScript 部分添加上述函数
   - 修改 `loadLogs` 函数以包含复选框

3. 重启服务器后即可使用删除日志功能

## 功能特性

- ✅ 单选/多选日志进行删除
- ✅ 全选功能
- ✅ 清空所有日志
- ✅ 删除操作会记录审计日志
- ✅ 确认对话框防止误操作
- ✅ 实时显示选中数量
