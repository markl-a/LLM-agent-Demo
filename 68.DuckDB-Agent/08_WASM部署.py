"""
DuckDB-Agent 示例 08: WASM 部署

展示 DuckDB 在瀏覽器中運行的能力：
1. WASM 版本介紹
2. 瀏覽器中的 DuckDB
3. JavaScript 集成
4. 前端數據分析應用
5. 離線數據處理
6. 實際部署示例
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from pathlib import Path

console = Console()


def introduce_duckdb_wasm():
    """介紹 DuckDB WASM"""
    console.print("\n[bold cyan]1. DuckDB WASM 簡介[/bold cyan]")

    intro = """
DuckDB-Wasm 是 DuckDB 的 WebAssembly 版本，可以直接在瀏覽器中運行。

核心特性:
- 完整的 SQL 功能，與桌面版一致
- 在瀏覽器中進行高性能數據分析
- 無需服務器，完全客戶端運行
- 支持 Parquet、CSV、JSON 等格式
- 與 Apache Arrow 集成
- 支持多線程（Web Workers）

適用場景:
- 數據可視化儀表板
- 離線數據分析工具
- 嵌入式 BI 應用
- 數據探索工具
- 教育和演示
"""

    console.print(Panel(intro, title="DuckDB-Wasm", border_style="cyan"))

    console.print("\n[yellow]安裝方式:[/yellow]")
    console.print("""
# npm 安裝
npm install @duckdb/duckdb-wasm

# 或使用 CDN
<script src="https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest"></script>
    """)


def show_basic_html_example():
    """展示基本 HTML 示例"""
    console.print("\n[bold cyan]2. 基本 HTML 集成[/bold cyan]")

    html_code = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DuckDB-Wasm 示例</title>
    <script src="https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest/dist/duckdb-mvp.wasm.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest/dist/duckdb-browser-mvp.worker.js"></script>
</head>
<body>
    <h1>DuckDB 瀏覽器版演示</h1>
    <button onclick="runQuery()">執行查詢</button>
    <div id="results"></div>

    <script type="module">
        import * as duckdb from 'https://cdn.jsdelivr.net/npm/@duckdb/duckdb-wasm@latest/+esm';

        let db;

        async function initDB() {
            const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();

            // 選擇bundle
            const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

            // 實例化
            const worker = new Worker(bundle.mainWorker);
            const logger = new duckdb.ConsoleLogger();
            db = new duckdb.AsyncDuckDB(logger, worker);
            await db.instantiate(bundle.mainModule, bundle.pthreadWorker);

            console.log('DuckDB 初始化成功！');
        }

        window.runQuery = async function() {
            if (!db) {
                await initDB();
            }

            // 創建連接
            const conn = await db.connect();

            // 執行查詢
            const result = await conn.query(`
                SELECT
                    'Hello from DuckDB-Wasm!' as message,
                    42 as answer,
                    CURRENT_DATE as today
            `);

            // 顯示結果
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<pre>' + JSON.stringify(result.toArray(), null, 2) + '</pre>';

            await conn.close();
        }

        // 頁面加載時初始化
        initDB();
    </script>
</body>
</html>"""

    syntax = Syntax(html_code, "html", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="basic_example.html", border_style="green"))


def show_data_analysis_example():
    """展示數據分析應用示例"""
    console.print("\n[bold cyan]3. 數據分析應用示例[/bold cyan]")

    js_code = """// data-analysis.js
import * as duckdb from '@duckdb/duckdb-wasm';

class DuckDBAnalyzer {
    constructor() {
        this.db = null;
        this.conn = null;
    }

    async initialize() {
        // 加載 DuckDB bundles
        const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
        const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

        // 創建 worker
        const worker = new Worker(bundle.mainWorker);
        const logger = new duckdb.ConsoleLogger();

        // 實例化數據庫
        this.db = new duckdb.AsyncDuckDB(logger, worker);
        await this.db.instantiate(bundle.mainModule, bundle.pthreadWorker);

        // 創建連接
        this.conn = await this.db.connect();

        console.log('DuckDB 分析器初始化完成');
    }

    async loadCSV(url) {
        // 註冊 HTTP 文件系統
        await this.db.registerFileURL('data.csv', url, duckdb.DuckDBDataProtocol.HTTP);

        // 創建表
        await this.conn.query(`
            CREATE TABLE sales AS
            SELECT * FROM read_csv_auto('data.csv')
        `);

        console.log('CSV 數據加載完成');
    }

    async loadParquet(url) {
        // 直接查詢遠程 Parquet 文件
        await this.db.registerFileURL('data.parquet', url, duckdb.DuckDBDataProtocol.HTTP);

        const result = await this.conn.query(`
            SELECT * FROM 'data.parquet' LIMIT 10
        `);

        return result.toArray();
    }

    async analyzeSales() {
        // 執行複雜分析
        const result = await this.conn.query(`
            SELECT
                category,
                COUNT(*) as sales_count,
                SUM(amount) as total_revenue,
                AVG(amount) as avg_sale
            FROM sales
            GROUP BY category
            ORDER BY total_revenue DESC
        `);

        return result.toArray();
    }

    async exportToArrow() {
        // 導出為 Arrow 格式
        const arrowResult = await this.conn.query(`
            SELECT * FROM sales
        `);

        return arrowResult;
    }

    async close() {
        if (this.conn) await this.conn.close();
        if (this.db) await this.db.terminate();
    }
}

// 使用示例
async function main() {
    const analyzer = new DuckDBAnalyzer();
    await analyzer.initialize();

    // 加載數據
    await analyzer.loadCSV('https://example.com/sales.csv');

    // 執行分析
    const results = await analyzer.analyzeSales();
    console.table(results);

    // 清理
    await analyzer.close();
}

main().catch(console.error);"""

    syntax = Syntax(js_code, "javascript", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="data-analysis.js", border_style="blue"))


def show_react_integration():
    """展示 React 集成示例"""
    console.print("\n[bold cyan]4. React 集成示例[/bold cyan]")

    react_code = """// DuckDBProvider.jsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import * as duckdb from '@duckdb/duckdb-wasm';

const DuckDBContext = createContext(null);

export function DuckDBProvider({ children }) {
    const [db, setDb] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function initDB() {
            try {
                const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
                const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);

                const worker = new Worker(bundle.mainWorker);
                const logger = new duckdb.ConsoleLogger();

                const database = new duckdb.AsyncDuckDB(logger, worker);
                await database.instantiate(bundle.mainModule, bundle.pthreadWorker);

                setDb(database);
                setLoading(false);
            } catch (error) {
                console.error('DuckDB 初始化失敗:', error);
            }
        }

        initDB();

        return () => {
            if (db) db.terminate();
        };
    }, []);

    return (
        <DuckDBContext.Provider value={{ db, loading }}>
            {children}
        </DuckDBContext.Provider>
    );
}

export function useDuckDB() {
    const context = useContext(DuckDBContext);
    if (!context) {
        throw new Error('useDuckDB must be used within DuckDBProvider');
    }
    return context;
}

// DataTable.jsx - 使用 DuckDB 的組件
export function DataTable({ query }) {
    const { db, loading } = useDuckDB();
    const [data, setData] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function executeQuery() {
            if (!db || loading) return;

            try {
                const conn = await db.connect();
                const result = await conn.query(query);
                setData(result.toArray());
                await conn.close();
            } catch (err) {
                setError(err.message);
            }
        }

        executeQuery();
    }, [db, loading, query]);

    if (loading) return <div>載入中...</div>;
    if (error) return <div>錯誤: {error}</div>;

    return (
        <table>
            <thead>
                <tr>
                    {data[0] && Object.keys(data[0]).map(key => (
                        <th key={key}>{key}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {data.map((row, idx) => (
                    <tr key={idx}>
                        {Object.values(row).map((val, i) => (
                            <td key={i}>{String(val)}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

// App.jsx - 主應用
function App() {
    return (
        <DuckDBProvider>
            <div className="App">
                <h1>DuckDB-Wasm 數據分析</h1>
                <DataTable query="SELECT * FROM generate_series(1, 10) AS t(id)" />
            </div>
        </DuckDBProvider>
    );
}"""

    syntax = Syntax(react_code, "javascript", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="React Integration", border_style="magenta"))


def show_advanced_features():
    """展示高級功能"""
    console.print("\n[bold cyan]5. 高級功能示例[/bold cyan]")

    advanced_code = """// advanced-features.js

// 1. 多線程支持
async function useMultipleThreads() {
    const db = new duckdb.AsyncDuckDB(logger, worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);

    // 設置線程數
    const conn = await db.connect();
    await conn.query('SET threads TO 4');

    // 並行查詢
    const result = await conn.query(`
        SELECT * FROM large_table
        WHERE condition
        ORDER BY column
    `);
}

// 2. 內存管理
async function memoryManagement() {
    const conn = await db.connect();

    // 設置內存限制
    await conn.query('SET memory_limit = "1GB"');

    // 檢查內存使用
    const memUsage = await conn.query(`
        SELECT * FROM duckdb_memory()
    `);
}

// 3. 插件擴展
async function loadExtensions() {
    const conn = await db.connect();

    // 安裝和加載擴展
    await conn.query('INSTALL httpfs');
    await conn.query('LOAD httpfs');

    // 現在可以查詢 HTTP 資源
    const result = await conn.query(`
        SELECT * FROM 'https://example.com/data.parquet'
    `);
}

// 4. 增量更新
async function incrementalUpdates() {
    const conn = await db.connect();

    // 創建表
    await conn.query(`
        CREATE TABLE metrics (
            timestamp TIMESTAMP,
            value DOUBLE,
            metric_name VARCHAR
        )
    `);

    // 增量插入數據
    setInterval(async () => {
        await conn.query(`
            INSERT INTO metrics VALUES
            (CURRENT_TIMESTAMP, random() * 100, 'cpu_usage')
        `);
    }, 1000);

    // 實時查詢
    const results = await conn.query(`
        SELECT
            DATE_TRUNC('minute', timestamp) as minute,
            AVG(value) as avg_value
        FROM metrics
        WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '5 minutes'
        GROUP BY minute
        ORDER BY minute DESC
    `);
}

// 5. 與 Observable Plot 集成
import * as Plot from "@observablehq/plot";

async function createVisualization() {
    const conn = await db.connect();

    const result = await conn.query(`
        SELECT
            date,
            SUM(sales) as total_sales
        FROM sales_data
        GROUP BY date
        ORDER BY date
    `);

    const data = result.toArray();

    return Plot.plot({
        marks: [
            Plot.line(data, {x: "date", y: "total_sales"}),
            Plot.dot(data, {x: "date", y: "total_sales"})
        ]
    });
}

// 6. 文件上傳處理
async function handleFileUpload(file) {
    const conn = await db.connect();

    // 註冊文件
    await db.registerFileHandle(
        file.name,
        file,
        duckdb.DuckDBDataProtocol.BROWSER_FILEREADER,
        true
    );

    // 查詢文件
    const result = await conn.query(`
        SELECT * FROM '${file.name}'
        LIMIT 100
    `);

    return result.toArray();
}"""

    syntax = Syntax(advanced_code, "javascript", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="advanced-features.js", border_style="yellow"))


def show_deployment_guide():
    """展示部署指南"""
    console.print("\n[bold cyan]6. 部署指南[/bold cyan]")

    deployment = """
部署步驟:

1. 安裝依賴
   npm install @duckdb/duckdb-wasm

2. 配置 Webpack/Vite
   # Vite 配置示例
   export default {
     optimizeDeps: {
       exclude: ['@duckdb/duckdb-wasm']
     },
     worker: {
       format: 'es'
     }
   }

3. 靜態資源配置
   - 確保 .wasm 文件被正確服務
   - 設置正確的 MIME 類型
   - 啟用 CORS（如果需要）

4. 生產優化
   - 使用 CDN 加載 DuckDB bundles
   - 啟用 gzip/brotli 壓縮
   - 實現懶加載策略
   - 緩存策略配置

5. 性能優化
   - 使用 Web Workers
   - 啟用多線程（如果瀏覽器支持）
   - 預加載常用數據
   - 實現查詢緩存

部署平台:
- Vercel
- Netlify
- GitHub Pages
- Cloudflare Pages
- 任何靜態網站託管服務

注意事項:
- 某些瀏覽器可能不支持 SharedArrayBuffer
- 需要設置 Cross-Origin-Opener-Policy 和 Cross-Origin-Embedder-Policy headers
- 移動端瀏覽器性能可能受限
"""

    console.print(Panel(deployment, title="部署指南", border_style="green"))


def create_example_files():
    """創建示例文件"""
    console.print("\n[bold cyan]7. 創建示例文件[/bold cyan]")

    try:
        # 創建示例目錄
        example_dir = Path("./duckdb-wasm-examples")
        example_dir.mkdir(parents=True, exist_ok=True)

        # package.json
        package_json = """{
  "name": "duckdb-wasm-demo",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@duckdb/duckdb-wasm": "^1.28.0"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}"""

        # index.html
        index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>DuckDB-Wasm Demo</title>
</head>
<body>
    <h1>DuckDB-Wasm 演示</h1>
    <div id="app"></div>
    <script type="module" src="/main.js"></script>
</body>
</html>"""

        # main.js
        main_js = """import * as duckdb from '@duckdb/duckdb-wasm';

async function main() {
    const BUNDLES = duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(BUNDLES);
    const worker = new Worker(bundle.mainWorker);
    const logger = new duckdb.ConsoleLogger();
    const db = new duckdb.AsyncDuckDB(logger, worker);
    await db.instantiate(bundle.mainModule);

    const conn = await db.connect();
    const result = await conn.query('SELECT 42 as answer');
    console.table(result.toArray());

    document.getElementById('app').innerHTML =
        '<pre>' + JSON.stringify(result.toArray(), null, 2) + '</pre>';
}

main();"""

        # 寫入文件
        (example_dir / "package.json").write_text(package_json, encoding='utf-8')
        (example_dir / "index.html").write_text(index_html, encoding='utf-8')
        (example_dir / "main.js").write_text(main_js, encoding='utf-8')

        console.print(f"[green]✓ 示例文件已創建到: {example_dir.absolute()}[/green]")
        console.print("\n運行命令:")
        console.print(f"  cd {example_dir}")
        console.print("  npm install")
        console.print("  npm run dev")

    except Exception as e:
        console.print(f"[red]✗ 創建示例文件失敗: {e}[/red]")


def main():
    """主函數"""
    console.print("\n[bold magenta]═══════════════════════════════════════[/bold magenta]")
    console.print("[bold magenta]   DuckDB WASM 部署示例   [/bold magenta]")
    console.print("[bold magenta]═══════════════════════════════════════[/bold magenta]")

    # 1. 介紹
    introduce_duckdb_wasm()

    # 2. HTML 示例
    show_basic_html_example()

    # 3. 數據分析示例
    show_data_analysis_example()

    # 4. React 集成
    show_react_integration()

    # 5. 高級功能
    show_advanced_features()

    # 6. 部署指南
    show_deployment_guide()

    # 7. 創建示例文件
    create_example_files()

    console.print("\n[bold green]✓ DuckDB-Wasm 部署示例完成！[/bold green]")

    console.print("\n[yellow]DuckDB-Wasm 優勢:[/yellow]")
    console.print("  - 完全在瀏覽器中運行，無需後端")
    console.print("  - 高性能數據分析（接近原生速度）")
    console.print("  - 支持大型數據集（GB 級）")
    console.print("  - 離線工作能力")
    console.print("  - 與現代前端框架無縫集成")
    console.print("  - 隱私保護（數據不離開客戶端）")

    console.print("\n[yellow]參考資源:[/yellow]")
    console.print("  - 官方文檔: https://duckdb.org/docs/api/wasm/overview")
    console.print("  - GitHub: https://github.com/duckdb/duckdb-wasm")
    console.print("  - 示例: https://shell.duckdb.org/")


if __name__ == "__main__":
    main()
