#!/usr/bin/env python3
"""
Goose 與 IDE 整合示例

展示如何將 Goose 整合到開發環境:
1. VS Code 整合
2. JetBrains IDE 整合
3. Vim/Neovim 整合
4. 自定義編輯器整合
5. 最佳實踐

作者: AI Agent
日期: 2024
"""

from typing import Dict, List


class IDEIntegrationDemo:
    """IDE 整合演示"""

    def __init__(self):
        """初始化"""
        pass

    def vscode_integration(self):
        """
        VS Code 整合
        """
        print("\n" + "="*70)
        print("VS Code 整合")
        print("="*70)

        # Tasks 配置
        tasks_json = """{
  // .vscode/tasks.json
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Goose: 代碼審查",
      "type": "shell",
      "command": "goose",
      "args": [
        "審查當前打開的文件 ${file}，檢查質量和安全性"
      ],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Goose: 生成測試",
      "type": "shell",
      "command": "goose",
      "args": [
        "為 ${file} 生成完整的單元測試"
      ],
      "problemMatcher": []
    },
    {
      "label": "Goose: 添加文檔",
      "type": "shell",
      "command": "goose",
      "args": [
        "為 ${file} 添加 docstring 和註釋"
      ],
      "problemMatcher": []
    },
    {
      "label": "Goose: 重構代碼",
      "type": "shell",
      "command": "goose",
      "args": [
        "重構 ${file}，提高可讀性和性能"
      ],
      "problemMatcher": []
    },
    {
      "label": "Goose: 解釋選中代碼",
      "type": "shell",
      "command": "bash",
      "args": [
        "-c",
        "goose '解釋以下代碼的功能：' && pbpaste | goose"
      ],
      "problemMatcher": []
    },
    {
      "label": "Goose: 優化性能",
      "type": "shell",
      "command": "goose",
      "args": [
        "分析 ${file} 的性能瓶頸並優化"
      ],
      "problemMatcher": []
    },
    {
      "label": "Goose: 安全檢查",
      "type": "shell",
      "command": "goose",
      "args": [
        "掃描 ${file} 的安全漏洞"
      ],
      "problemMatcher": []
    }
  ]
}"""

        print("\n📝 Tasks 配置:")
        print("-"*70)
        print(tasks_json)

        # Keybindings 配置
        keybindings_json = """{
  // .vscode/keybindings.json
  "keybindings": [
    {
      "key": "ctrl+shift+g r",
      "command": "workbench.action.tasks.runTask",
      "args": "Goose: 代碼審查"
    },
    {
      "key": "ctrl+shift+g t",
      "command": "workbench.action.tasks.runTask",
      "args": "Goose: 生成測試"
    },
    {
      "key": "ctrl+shift+g d",
      "command": "workbench.action.tasks.runTask",
      "args": "Goose: 添加文檔"
    },
    {
      "key": "ctrl+shift+g f",
      "command": "workbench.action.tasks.runTask",
      "args": "Goose: 重構代碼"
    },
    {
      "key": "ctrl+shift+g e",
      "command": "workbench.action.tasks.runTask",
      "args": "Goose: 解釋選中代碼"
    }
  ]
}"""

        print("\n⌨️ 快捷鍵配置:")
        print("-"*70)
        print(keybindings_json)

        # Settings 配置
        settings_json = """{
  // .vscode/settings.json
  "terminal.integrated.env.linux": {
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  },
  "terminal.integrated.env.osx": {
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  },
  "terminal.integrated.env.windows": {
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  },

  // 自定義代碼片段
  "editor.snippetSuggestions": "top",

  // 任務自動檢測
  "task.autoDetect": "on",

  // 終端配置
  "terminal.integrated.defaultProfile.linux": "bash",

  // Python 配置（如果使用 Python）
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",

  // 文件監視
  "files.watcherExclude": {
    "**/.goose/**": true
  }
}"""

        print("\n⚙️ Settings 配置:")
        print("-"*70)
        print(settings_json)

        # 自定義代碼片段
        snippets = """{
  // .vscode/goose.code-snippets
  "Goose Review": {
    "prefix": "goose-review",
    "body": [
      "# Goose AI 代碼審查",
      "# 運行: Ctrl+Shift+G R"
    ],
    "description": "添加 Goose 審查標記"
  },
  "Goose TODO": {
    "prefix": "goose-todo",
    "body": [
      "# TODO (Goose): ${1:描述任務}",
      "# 使用 Goose 處理: goose '${1}'"
    ],
    "description": "添加 Goose TODO 標記"
  },
  "Goose Test": {
    "prefix": "goose-test",
    "body": [
      "# 測試由 Goose AI 生成",
      "def test_${1:function_name}():",
      "    ${2:pass}"
    ],
    "description": "Goose 測試模板"
  }
}"""

        print("\n📄 代碼片段:")
        print("-"*70)
        print(snippets)

        # VS Code 擴展腳本
        extension_script = """// Goose VS Code 擴展（概念）
// extension.ts

import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    // 註冊審查命令
    let reviewCommand = vscode.commands.registerCommand(
        'goose.review',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;

            const filePath = editor.document.fileName;

            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Goose AI 正在審查代碼...",
                cancellable: false
            }, async (progress) => {
                const result = await runGoose(
                    `審查 ${filePath} 的代碼質量`
                );

                // 顯示結果
                showReviewResults(result);
            });
        }
    );

    // 註冊快速修復提供器
    let quickFixProvider = vscode.languages.registerCodeActionsProvider(
        { scheme: 'file', language: 'python' },
        new GooseQuickFixProvider(),
        { providedCodeActionKinds: [vscode.CodeActionKind.QuickFix] }
    );

    context.subscriptions.push(reviewCommand, quickFixProvider);
}

class GooseQuickFixProvider implements vscode.CodeActionProvider {
    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        // Goose 重構建議
        const refactorAction = new vscode.CodeAction(
            '🪿 Goose: 重構此代碼',
            vscode.CodeActionKind.Refactor
        );
        refactorAction.command = {
            command: 'goose.refactor',
            title: 'Goose 重構',
            arguments: [document, range]
        };
        actions.push(refactorAction);

        return actions;
    }
}

async function runGoose(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
        exec(`goose "${prompt}"`, (error, stdout, stderr) => {
            if (error) reject(error);
            else resolve(stdout);
        });
    });
}"""

        print("\n🔌 VS Code 擴展示例:")
        print("-"*70)
        print(extension_script)

    def jetbrains_integration(self):
        """
        JetBrains IDE 整合
        """
        print("\n" + "="*70)
        print("JetBrains IDE 整合（PyCharm, IntelliJ, etc.）")
        print("="*70)

        # External Tools 配置
        external_tools = """<!-- External Tools 配置 -->
<!-- Settings → Tools → External Tools -->

1. Goose 代碼審查
   Name: Goose Review
   Program: goose
   Arguments: "審查 $FilePath$ 的代碼質量"
   Working directory: $ProjectFileDir$
   Advanced Options:
     ✓ Synchronize files after execution
     ✓ Open console for tool output

2. Goose 生成測試
   Name: Goose Generate Tests
   Program: goose
   Arguments: "為 $FilePath$ 生成單元測試"
   Working directory: $ProjectFileDir$

3. Goose 添加文檔
   Name: Goose Add Docs
   Program: goose
   Arguments: "為 $FilePath$ 添加 docstring"
   Working directory: $ProjectFileDir$

4. Goose 解釋代碼
   Name: Goose Explain
   Program: bash
   Arguments: -c "echo '$SelectedText$' | goose '解釋這段代碼'"
   Working directory: $ProjectFileDir$

快捷鍵設置：
Settings → Keymap → External Tools
- Goose Review: Ctrl+Shift+G, R
- Goose Generate Tests: Ctrl+Shift+G, T
- Goose Add Docs: Ctrl+Shift+G, D
"""

        print("\n⚙️ External Tools 配置:")
        print("-"*70)
        print(external_tools)

        # File Watchers 配置
        file_watchers = """<!-- File Watchers 配置 -->
<!-- Settings → Tools → File Watchers -->

<component name="ProjectFileWatchers">
  <watcher>
    <name>Goose Auto Review</name>
    <file_types>Python</file_types>
    <scope>Project Files</scope>
    <program>goose</program>
    <arguments>"快速審查 $FilePath$"</arguments>
    <working_dir>$ProjectFileDir$</working_dir>
    <envs />
    <output_paths_to_refresh />
    <other_options />
  </watcher>

  <watcher>
    <name>Goose Auto Format</name>
    <file_types>Python</file_types>
    <scope>Changed Files</scope>
    <program>goose</program>
    <arguments>"格式化並優化 $FilePath$"</arguments>
    <working_dir>$ProjectFileDir$</working_dir>
  </watcher>
</component>"""

        print("\n👁️ File Watchers:")
        print("-"*70)
        print(file_watchers)

        # Live Templates
        live_templates = """<!-- Live Templates 配置 -->
<!-- Settings → Editor → Live Templates -->

新建模板組: Goose

模板 1: goosereview
Abbreviation: greview
Template text:
# Goose AI 審查標記
# 運行: Tools → External Tools → Goose Review
$END$

模板 2: goosetodo
Abbreviation: gtodo
Template text:
# TODO (Goose): $DESCRIPTION$
# 命令: goose "$DESCRIPTION$"
$END$

Variables:
  DESCRIPTION - complete()

模板 3: goosetest
Abbreviation: gtest
Template text:
# 測試由 Goose AI 生成
def test_$NAME$():
    \"\"\"測試 $NAME$ 函數\"\"\"
    $END$
    pass

Variables:
  NAME - complete()
"""

        print("\n📝 Live Templates:")
        print("-"*70)
        print(live_templates)

    def vim_neovim_integration(self):
        """
        Vim/Neovim 整合
        """
        print("\n" + "="*70)
        print("Vim/Neovim 整合")
        print("="*70)

        # Vim 配置
        vimrc = """\" Goose AI 整合配置
\" ~/.vimrc 或 ~/.config/nvim/init.vim

\" 基本映射
\" 審查當前文件
nnoremap <leader>gr :!goose "審查 % 的代碼質量"<CR>

\" 生成測試
nnoremap <leader>gt :!goose "為 % 生成單元測試"<CR>

\" 添加文檔
nnoremap <leader>gd :!goose "為 % 添加文檔"<CR>

\" 解釋選中的代碼
vnoremap <leader>ge :<C-U>call GooseExplain()<CR>

function! GooseExplain()
    let l:selected = GetVisualSelection()
    let l:prompt = "解釋以下代碼:\\n" . l:selected
    execute '!goose "' . l:prompt . '"'
endfunction

function! GetVisualSelection()
    let [line_start, column_start] = getpos("'<")[1:2]
    let [line_end, column_end] = getpos("'>")[1:2]
    let lines = getline(line_start, line_end)
    return join(lines, "\\n")
endfunction

\" 重構當前函數
nnoremap <leader>gf :call GooseRefactorFunction()<CR>

function! GooseRefactorFunction()
    let l:save_cursor = getpos('.')
    normal! [[
    let l:start = line('.')
    normal! ][
    let l:end = line('.')

    let l:func = join(getline(l:start, l:end), "\\n")
    let l:prompt = "重構以下函數:\\n" . l:func

    execute '!goose "' . l:prompt . '"'
    call setpos('.', l:save_cursor)
endfunction

\" 異步執行 Goose（Neovim）
if has('nvim')
    function! GooseAsync(prompt)
        let l:bufnr = nvim_create_buf(v:false, v:true)
        call nvim_buf_set_option(bufnr, 'buftype', 'nofile')
        call nvim_buf_set_name(bufnr, 'Goose Output')

        let l:job = jobstart(['goose', a:prompt], {
            \\ 'on_stdout': {j, d, e -> nvim_buf_set_lines(bufnr, -1, -1, v:false, d)},
            \\ 'on_stderr': {j, d, e -> nvim_buf_set_lines(bufnr, -1, -1, v:false, d)},
        \\ })

        execute 'split | buffer' . bufnr
    endfunction

    nnoremap <leader>ga :call GooseAsync("審查當前項目")<CR>
endif

\" 命令定義
command! -nargs=1 Goose !goose <args>
command! GooseReview !goose "審查 % 的代碼"
command! GooseTest !goose "為 % 生成測試"
command! GooseDocs !goose "為 % 生成文檔"
"""

        print("\n📝 Vim 配置:")
        print("-"*70)
        print(vimrc)

        # Neovim Lua 配置
        lua_config = """-- Goose AI 整合 (Neovim Lua)
-- ~/.config/nvim/lua/goose.lua

local M = {}

-- 運行 Goose 命令
function M.run(prompt)
    local cmd = string.format('goose "%s"', prompt)
    vim.cmd('!' .. cmd)
end

-- 審查當前文件
function M.review()
    local file = vim.fn.expand('%:p')
    M.run(string.format('審查 %s 的代碼質量', file))
end

-- 生成測試
function M.generate_tests()
    local file = vim.fn.expand('%:p')
    M.run(string.format('為 %s 生成單元測試', file))
end

-- 添加文檔
function M.add_docs()
    local file = vim.fn.expand('%:p')
    M.run(string.format('為 %s 添加文檔', file))
end

-- 解釋選中的代碼
function M.explain_selection()
    local lines = vim.fn.getline("'<", "'>")
    local code = table.concat(lines, "\\n")
    M.run(string.format('解釋以下代碼:\\n%s', code))
end

-- 異步運行
function M.run_async(prompt)
    local bufnr = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_name(bufnr, 'Goose Output')

    local lines = {}
    vim.fn.jobstart({'goose', prompt}, {
        on_stdout = function(_, data)
            vim.list_extend(lines, data)
            vim.api.nvim_buf_set_lines(bufnr, 0, -1, false, lines)
        end,
        on_exit = function()
            vim.api.nvim_buf_set_option(bufnr, 'modifiable', false)
        end,
    })

    vim.cmd('split')
    vim.api.nvim_set_current_buf(bufnr)
end

-- 設置快捷鍵
function M.setup()
    local opts = { noremap = true, silent = true }

    vim.keymap.set('n', '<leader>gr', M.review, opts)
    vim.keymap.set('n', '<leader>gt', M.generate_tests, opts)
    vim.keymap.set('n', '<leader>gd', M.add_docs, opts)
    vim.keymap.set('v', '<leader>ge', M.explain_selection, opts)

    -- 命令
    vim.api.nvim_create_user_command('GooseReview', M.review, {})
    vim.api.nvim_create_user_command('GooseTest', M.generate_tests, {})
    vim.api.nvim_create_user_command('GooseDocs', M.add_docs, {})
    vim.api.nvim_create_user_command('Goose',
        function(opts) M.run(opts.args) end,
        { nargs = 1 }
    )
end

return M

-- 在 init.lua 中使用:
-- require('goose').setup()
"""

        print("\n🌙 Neovim Lua 配置:")
        print("-"*70)
        print(lua_config)

    def emacs_integration(self):
        """
        Emacs 整合
        """
        print("\n" + "="*70)
        print("Emacs 整合")
        print("="*70)

        emacs_lisp = """;;; goose.el --- Goose AI integration for Emacs

;;; Code:

(defun goose-run (prompt)
  "Run Goose with PROMPT."
  (interactive "sGoose prompt: ")
  (let ((output-buffer (get-buffer-create "*Goose Output*")))
    (with-current-buffer output-buffer
      (erase-buffer))
    (start-process "goose" output-buffer "goose" prompt)
    (display-buffer output-buffer)))

(defun goose-review-file ()
  "Review current file with Goose."
  (interactive)
  (goose-run (format "審查 %s 的代碼質量" (buffer-file-name))))

(defun goose-generate-tests ()
  "Generate tests for current file."
  (interactive)
  (goose-run (format "為 %s 生成單元測試" (buffer-file-name))))

(defun goose-add-docs ()
  "Add documentation to current file."
  (interactive)
  (goose-run (format "為 %s 添加文檔" (buffer-file-name))))

(defun goose-explain-region (start end)
  "Explain selected code region from START to END."
  (interactive "r")
  (let ((code (buffer-substring-no-properties start end)))
    (goose-run (format "解釋以下代碼:\\n%s" code))))

;; 快捷鍵綁定
(global-set-key (kbd "C-c g r") 'goose-review-file)
(global-set-key (kbd "C-c g t") 'goose-generate-tests)
(global-set-key (kbd "C-c g d") 'goose-add-docs)
(global-set-key (kbd "C-c g e") 'goose-explain-region)

(provide 'goose)
;;; goose.el ends here

;; 在 init.el 中添加:
;; (require 'goose)
"""

        print("\n📝 Emacs 配置:")
        print("-"*70)
        print(emacs_lisp)

    def custom_integration_guide(self):
        """
        自定義編輯器整合指南
        """
        print("\n" + "="*70)
        print("自定義編輯器整合指南")
        print("="*70)

        guide = """
整合 Goose 到任何編輯器的步驟:

1. 執行外部命令
   - 所有編輯器都支持執行 shell 命令
   - 使用: goose "your prompt"

2. 獲取文件路徑
   - 需要當前文件的完整路徑
   - 傳遞給 Goose: goose "審查 /path/to/file.py"

3. 獲取選中文本
   - 讀取用戶選中的代碼
   - 作為提示的一部分發送給 Goose

4. 顯示輸出
   - 在新窗口/緩衝區顯示 Goose 的輸出
   - 或集成到編輯器的輸出面板

5. 異步執行（可選）
   - 對於耗時任務，使用異步執行
   - 避免阻塞編輯器

6. 添加快捷鍵
   - 綁定常用操作到快捷鍵
   - 提高使用效率

7. 創建命令
   - 封裝常用的 Goose 操作
   - 簡化調用

示例（偽代碼）:
```
function runGoose(prompt):
    command = "goose '" + prompt + "'"
    output = executeShellCommand(command)
    showInNewBuffer(output)

function reviewCurrentFile():
    filePath = getCurrentFilePath()
    prompt = "審查 " + filePath + " 的代碼質量"
    runGoose(prompt)

bindKey("Ctrl+Shift+G R", reviewCurrentFile)
```

常用的整合功能:
1. 代碼審查
2. 生成測試
3. 添加文檔
4. 解釋代碼
5. 重構建議
6. 安全檢查
7. 性能優化
"""

        print(guide)

    def best_practices(self):
        """
        IDE 整合最佳實踐
        """
        print("\n" + "="*70)
        print("IDE 整合最佳實踐")
        print("="*70)

        practices = """
1. 快捷鍵設計
   ✓ 使用一致的前綴（如 Ctrl+Shift+G）
   ✓ 第二個鍵表示功能（R=Review, T=Test, D=Docs）
   ✓ 避免與現有快捷鍵衝突

2. 用戶反饋
   ✓ 顯示進度指示器（特別是耗時操作）
   ✓ 清晰的錯誤消息
   ✓ 成功完成的通知

3. 輸出管理
   ✓ 在專用窗口/面板顯示輸出
   ✓ 支持語法高亮（如果是代碼）
   ✓ 允許複製/保存輸出

4. 性能優化
   ✓ 異步執行長時間任務
   ✓ 緩存常用結果
   ✓ 提供取消操作的選項

5. 錯誤處理
   ✓ 檢查 Goose 是否已安裝
   ✓ 驗證 API Key 是否設置
   ✓ 處理網絡錯誤

6. 配置管理
   ✓ 允許用戶配置 API Key
   ✓ 支持自定義提示模板
   ✓ 可配置快捷鍵

7. 上下文感知
   ✓ 識別文件類型
   ✓ 根據項目類型調整提示
   ✓ 使用項目特定的配置

8. 團隊協作
   ✓ 項目級配置可提交到版本控制
   ✓ 個人配置保持本地
   ✓ 提供配置示例

檢查清單:
□ Goose 命令可執行
□ 文件路徑正確傳遞
□ 輸出正確顯示
□ 快捷鍵工作正常
□ 錯誤處理完善
□ 有用戶文檔
□ 異步執行（如需要）
□ 配置選項完整
"""

        print(practices)


def main():
    """主函數"""
    print("="*70)
    print("Goose 與 IDE 整合教程")
    print("="*70)

    demo = IDEIntegrationDemo()

    sections = [
        ("VS Code 整合", demo.vscode_integration),
        ("JetBrains IDE", demo.jetbrains_integration),
        ("Vim/Neovim", demo.vim_neovim_integration),
        ("Emacs", demo.emacs_integration),
        ("自定義整合", demo.custom_integration_guide),
        ("最佳實踐", demo.best_practices),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. Goose 可整合到所有主流編輯器")
    print("2. 使用快捷鍵提高效率")
    print("3. 異步執行避免阻塞")
    print("4. 提供良好的用戶反饋")
    print("5. 遵循編輯器的慣例和最佳實踐")

    print("\n🎉 恭喜完成所有 Goose 教程！")
    print("\n建議:")
    print("- 從 README.md 開始全面了解 Goose")
    print("- 按順序學習所有教程文件")
    print("- 實踐整合到你的開發工作流")
    print("- 探索 Goose 的更多可能性")


if __name__ == "__main__":
    main()
