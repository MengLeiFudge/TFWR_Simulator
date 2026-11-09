# WSL 文件工具读取完整性

本页记录本项目在 Windows 盘上使用文件修改工具时的读取边界。适用于从完整文件快照生成新内容的 `edit`、`replace` 及同类操作。

## 完整性要求

在 WSL 的 Windows 挂载盘上修改文件时，不能把一次读取返回的字节数少于请求长度当作文件末尾。读取层必须继续读到 EOF，并核对实际总字节数与稳定的文件大小；发现不一致就拒绝写回。并发修改检查和版本哈希必须建立在完整字节上。

使用尚未满足上述要求的工具时，修改前保存完整原件，修改后用独立的完整读取核对字节差异。完成判据为：只出现预期变化，文件末尾、编码和换行完整。涉及真实存档时仍遵守 [存档边界](../AGENTS.md#存档与部署)。

## 本次证据

2026-11-09，修正 `__builtins__.py` 的三个彩色块名称时，临时候选发生真实磁盘截断。以下三处替换的字节长度均不变，因此完整结果应保持原文件大小。

| 项目 | 证据 |
| --- | --- |
| 原文件 | 66,722字节，2,855个CRLF；SHA256 `7c3d23a03b49816eb9080a957f2afbdca1e8cbe52d0c8ac47e2c4466396df1c7` |
| 正确完整结果 | 66,722字节；SHA256 `a409abd47ad2442c5878f2ba917ad5da4d3bb4449fd31f500e5bd3df5cc5a7e7` |
| 故障候选 | 65,512字节，2,800个CRLF；SHA256 `e10d750d9b317c83fd0be783734073edb19dcd6a21412757d8dbf6e055539793` |
| 字节归属 | 故障哈希与正确完整结果的前65,512字节完全相同，末尾丢失1,210字节 |
| 所属文件系统 | `/mnt/d` 为9p/DrvFs，挂载参数含 `msize=65536` |
| 所属运行时与插件 | Node.js v24.18.0；`@criogaid/pi-hashline-edit` 0.10.0 |
| 工具回执 | `publication=PUBLISHED`、`matches=3`，随后的SHA256命令成功 |

原件备份、完整修复与回读记录保存在 `.codex/underground-achievements/builtins-colors-fix/`。故障候选在恢复时已被完整候选覆盖；故障内容可由原件、三个等长替换及前缀长度精确确定，历史回执保留其哈希。

完整性校验在部署前阻止了故障候选。真实存档只接收了完整结果，见 [声明校正记录](achievement-validation.json)的 `external_stub_mismatch.correction`。

## 读取链路与缺口

插件的 `src/pi/file-read.ts` 中，`withFileRead()` 在非Windows系统以 `O_RDONLY | O_NONBLOCK` 打开文件。它对比读取前后的设备、inode、大小和时间戳，未验证回调是否读完全部字节。

`src/pi/file-commit.ts` 的 `readRegularFile()` 调用 `handle.readFile({ signal })`。`readEditableSnapshot()` 用该结果同时生成编辑文本和 `baseRevision`；`fileRevision()` 也使用相同读取函数。`src/pi/mutation-runner.ts` 的 `runTextMutation()` 把转换结果交给 `commitFile()`。`edit`、`replace` 共用这条读取与提交链路。

本机 Node.js 内置 `internal/fs/promises` 的 `readFileHandle()` 先按文件大小分配缓冲区；仅当大小超过 `kReadFileBufferLength`（512 KiB）时启用分块分支。以下结束条件也允许已知大小的小文件在一次短读后直接返回：

```javascript
bytesRead !== buffer.length && !chunkedRead && !noSize
```

因此，若已知大小66,722字节的文件首次只返回65,512字节，当前分支会把该前缀当作读取结果。9p挂载的消息大小为65,536字节，故障长度为该大小减24字节，符合短读传输边界。这里的64 KiB是文件系统传输边界证据，并非插件的输出预算。

该机制也解释了为什么版本检查和成功回执可能没有报警：若编辑快照及提交前的版本回读都只取得同一个前缀，它们的哈希仍会一致；文件元数据未变化也不能证明已经读完。以不完整快照计算的diff只包含三个改名，不一定显示被快照漏掉的末尾。

修复位置是插件的完整读取与快照层：循环读取至EOF或使用完整流读取，再检查字节总数；继续保留现有元数据与版本检查。仅调整模型输出预算不能补上读取完整性检查。

## 证据范围

本次核对了历史工具回执、完整备份、故障前缀哈希、挂载参数、已安装插件源码及其jiti转译缓存，以及本机Node内置源码。源码定位与故障字节边界一致。

没有采集故障瞬间的系统调用轨迹，没有新增复现测试，不能声称已实测复现该短读分支。读取内核头部常量的在线补证因 `SSL: UNEXPECTED_EOF_WHILE_READING` 失败，未以该次下载作为证据。Pi本体和第三方插件未修改；上游修复与修复后复验尚未执行。
