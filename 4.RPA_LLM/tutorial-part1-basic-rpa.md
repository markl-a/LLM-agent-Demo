# 實戰教程 Part 1：基礎 RPA 自動化

## 目錄

1. [環境準備](#環境準備)
2. [第一個 RPA 腳本](#第一個-rpa-腳本)
3. [瀏覽器自動化](#瀏覽器自動化)
4. [桌面應用自動化](#桌面應用自動化)
5. [資料處理自動化](#資料處理自動化)
6. [實戰專案：網頁數據採集](#實戰專案網頁數據採集)

---

## 環境準備

### 系統需求

- Python 3.8 或更高版本
- 8GB RAM（建議 16GB）
- 支援的作業系統：Windows、macOS、Linux

### 安裝 Python 與基礎工具

```bash
# 檢查 Python 版本
python --version  # 應該是 3.8+

# 建立虛擬環境
python -m venv rpa_env

# 啟動虛擬環境
# Windows
rpa_env\Scripts\activate
# macOS/Linux
source rpa_env/bin/activate

# 升級 pip
pip install --upgrade pip
```

### 安裝核心套件

```bash
# 安裝 RPA 基礎套件
pip install playwright selenium pyautogui

# 安裝數據處理套件
pip install pandas openpyxl python-docx

# 安裝 OCR 相關
pip install pytesseract pillow

# 安裝 Playwright 瀏覽器
playwright install

# 其他實用工具
pip install python-dotenv requests beautifulsoup4
```

### 專案結構設置

創建以下目錄結構：

```
rpa_project/
├── config/
│   └── settings.py          # 配置文件
├── data/
│   ├── input/               # 輸入數據
│   └── output/              # 輸出結果
├── logs/                    # 日誌文件
├── scripts/                 # RPA 腳本
│   ├── __init__.py
│   ├── web_automation.py
│   ├── desktop_automation.py
│   └── data_processing.py
├── utils/                   # 工具函數
│   ├── __init__.py
│   ├── logger.py
│   └── helpers.py
├── tests/                   # 測試文件
├── .env                     # 環境變數
├── requirements.txt         # 依賴清單
└── main.py                  # 主程式
```

創建基礎配置文件：

**config/settings.py**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent

# 數據目錄
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

# 確保目錄存在
for directory in [INPUT_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 瀏覽器設置
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))

# 日誌設置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

**utils/logger.py**
```python
import logging
from pathlib import Path
from datetime import datetime
from config.settings import LOG_DIR, LOG_LEVEL

def setup_logger(name: str) -> logging.Logger:
    """設置日誌記錄器"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # 避免重複添加 handler
    if logger.handlers:
        return logger

    # 文件 handler
    log_file = LOG_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

**.env**
```env
# 瀏覽器設置
HEADLESS=false
BROWSER_TIMEOUT=30000

# 日誌設置
LOG_LEVEL=INFO

# 其他設置
MAX_RETRIES=3
RETRY_DELAY=2
```

---

## 第一個 RPA 腳本

### Hello World 範例

創建 **scripts/hello_rpa.py**：

```python
"""
第一個 RPA 腳本：自動化 Hello World
功能：打開記事本並輸入文字
"""
import time
import pyautogui
from utils.logger import setup_logger

logger = setup_logger("hello_rpa")

def main():
    logger.info("開始執行 Hello RPA 腳本")

    try:
        # 1. 打開記事本（Windows）
        logger.info("打開記事本")
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write('notepad', interval=0.1)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        # 2. 輸入文字
        logger.info("輸入文字")
        text = """
        Hello, RPA World!

        This is my first RPA automation script.
        Created with Python and pyautogui.
        """
        pyautogui.write(text, interval=0.05)

        # 3. 格式化
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'a')  # 全選
        time.sleep(0.5)

        logger.info("腳本執行成功")

        # 4. 提示用戶
        print("\n腳本執行完成！記事本已打開並輸入文字。")
        print("按 Ctrl+C 結束程式...")

        # 保持程式運行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("用戶中斷執行")
    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

執行腳本：

```bash
python scripts/hello_rpa.py
```

### 關鍵概念解析

1. **pyautogui.press()**：模擬按鍵
2. **pyautogui.write()**：輸入文字
3. **pyautogui.hotkey()**：組合鍵
4. **time.sleep()**：等待延遲（重要！）

---

## 瀏覽器自動化

### 使用 Playwright

Playwright 是現代化的瀏覽器自動化工具，相比 Selenium 更快、更穩定。

**scripts/web_automation.py**

```python
"""
網頁自動化基礎範例
功能：搜尋引擎自動化
"""
from playwright.sync_api import sync_playwright, Page
from utils.logger import setup_logger
from config.settings import HEADLESS, BROWSER_TIMEOUT
import time

logger = setup_logger("web_automation")

class WebAutomation:
    def __init__(self, headless: bool = HEADLESS):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page: Page = None

    def __enter__(self):
        """上下文管理器：初始化"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=100  # 放慢操作以便觀察
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(BROWSER_TIMEOUT)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器：清理"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def search_google(self, query: str) -> list[dict]:
        """
        在 Google 搜尋並提取結果

        Args:
            query: 搜尋關鍵字

        Returns:
            搜尋結果列表
        """
        logger.info(f"搜尋關鍵字: {query}")

        # 1. 訪問 Google
        self.page.goto("https://www.google.com")
        logger.info("已訪問 Google 首頁")

        # 2. 同意 Cookie（如果出現）
        try:
            self.page.click('button:has-text("Accept all")', timeout=3000)
        except:
            pass

        # 3. 輸入搜尋關鍵字
        search_box = self.page.locator('textarea[name="q"]')
        search_box.fill(query)
        logger.info("已輸入搜尋關鍵字")

        # 4. 提交搜尋
        search_box.press("Enter")

        # 5. 等待結果載入
        self.page.wait_for_selector('#search')
        logger.info("搜尋結果已載入")

        # 6. 提取搜尋結果
        results = []
        search_results = self.page.locator('#search .g')

        for i in range(min(10, search_results.count())):
            try:
                result = search_results.nth(i)

                title_elem = result.locator('h3').first
                link_elem = result.locator('a').first

                if title_elem.count() > 0 and link_elem.count() > 0:
                    title = title_elem.inner_text()
                    link = link_elem.get_attribute('href')

                    results.append({
                        'rank': i + 1,
                        'title': title,
                        'link': link
                    })

            except Exception as e:
                logger.warning(f"提取第 {i+1} 個結果時出錯: {str(e)}")
                continue

        logger.info(f"成功提取 {len(results)} 個搜尋結果")
        return results

    def screenshot(self, path: str):
        """截圖"""
        self.page.screenshot(path=path, full_page=True)
        logger.info(f"截圖已保存: {path}")

def demo_google_search():
    """示範 Google 搜尋"""
    with WebAutomation(headless=False) as web:
        # 執行搜尋
        results = web.search_google("Python RPA automation")

        # 輸出結果
        print("\n搜尋結果:")
        print("=" * 80)
        for result in results:
            print(f"\n{result['rank']}. {result['title']}")
            print(f"   {result['link']}")

        # 截圖
        web.screenshot("data/output/google_search_result.png")

        # 等待觀察
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    demo_google_search()
```

### 使用 Selenium（備選方案）

**scripts/web_automation_selenium.py**

```python
"""
使用 Selenium 的網頁自動化
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from utils.logger import setup_logger

logger = setup_logger("selenium_automation")

class SeleniumAutomation:
    def __init__(self, headless: bool = False):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def fill_form_example(self, url: str):
        """表單填寫範例"""
        self.driver.get(url)

        # 等待表單載入
        name_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "name"))
        )

        # 填寫表單
        name_field.send_keys("John Doe")

        email_field = self.driver.find_element(By.ID, "email")
        email_field.send_keys("john@example.com")

        # 提交
        submit_btn = self.driver.find_element(By.ID, "submit")
        submit_btn.click()

        # 等待結果
        self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )

        logger.info("表單提交成功")
```

### 實用技巧

**1. 元素定位策略**

```python
# 多種定位方式
page.locator('#id')                    # ID
page.locator('.class')                 # Class
page.locator('button:has-text("登入")')  # 文字
page.locator('//xpath')                # XPath
page.locator('[data-testid="submit"]') # 屬性
```

**2. 等待策略**

```python
# 顯式等待
page.wait_for_selector('#element', state='visible')

# 等待網路閒置
page.wait_for_load_state('networkidle')

# 自定義等待
page.wait_for_function('() => document.readyState === "complete"')
```

**3. 錯誤處理**

```python
from playwright.sync_api import TimeoutError as PlaywrightTimeout

try:
    page.click('#submit', timeout=5000)
except PlaywrightTimeout:
    logger.error("元素點擊超時")
    page.screenshot(path="error.png")
    raise
```

---

## 桌面應用自動化

### 使用 PyAutoGUI

**scripts/desktop_automation.py**

```python
"""
桌面應用自動化
功能：Windows 計算機自動化
"""
import pyautogui
import time
from utils.logger import setup_logger

logger = setup_logger("desktop_automation")

# 設置安全機制：將滑鼠移到螢幕左上角會引發異常
pyautogui.FAILSAFE = True

class CalculatorAutomation:
    """Windows 計算機自動化"""

    def __init__(self):
        self.calc_window = None

    def open_calculator(self):
        """打開計算機"""
        logger.info("打開計算機")
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write('calc', interval=0.1)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)  # 等待計算機打開

    def calculate(self, expression: str) -> str:
        """
        執行計算

        Args:
            expression: 計算表達式，如 "2+3*4"

        Returns:
            計算結果
        """
        logger.info(f"計算表達式: {expression}")

        # 清除
        pyautogui.press('esc')
        time.sleep(0.3)

        # 輸入表達式
        for char in expression:
            if char.isdigit():
                pyautogui.press(char)
            elif char in ['+', '-', '*', '/']:
                # 映射運算符
                operator_map = {
                    '+': 'add',
                    '-': 'subtract',
                    '*': 'multiply',
                    '/': 'divide'
                }
                pyautogui.press(operator_map.get(char, char))
            time.sleep(0.2)

        # 按等號
        pyautogui.press('enter')
        time.sleep(0.5)

        # OCR 讀取結果（簡化版，實際需要使用 pytesseract）
        logger.info("計算完成")

    def close(self):
        """關閉計算機"""
        pyautogui.hotkey('alt', 'f4')
        logger.info("計算機已關閉")

def demo_calculator():
    """示範計算機自動化"""
    calc = CalculatorAutomation()

    try:
        calc.open_calculator()

        # 執行多個計算
        calculations = ["123+456", "999-333", "12*34"]

        for expr in calculations:
            print(f"\n計算: {expr}")
            calc.calculate(expr)
            time.sleep(2)

        input("\n按 Enter 關閉計算機...")
        calc.close()

    except Exception as e:
        logger.error(f"錯誤: {str(e)}", exc_info=True)

if __name__ == "__main__":
    demo_calculator()
```

### 圖像識別自動化

當無法使用元素定位時，可使用圖像識別：

```python
import pyautogui

# 尋找圖片位置
try:
    location = pyautogui.locateOnScreen('button.png', confidence=0.8)
    if location:
        # 點擊圖片中心
        pyautogui.click(pyautogui.center(location))
        logger.info(f"找到並點擊圖片: {location}")
except pyautogui.ImageNotFoundException:
    logger.error("找不到圖片")
```

---

## 資料處理自動化

### Excel 自動化

**scripts/data_processing.py**

```python
"""
資料處理自動化
功能：Excel 數據處理
"""
import pandas as pd
from pathlib import Path
from utils.logger import setup_logger
from config.settings import INPUT_DIR, OUTPUT_DIR

logger = setup_logger("data_processing")

class ExcelProcessor:
    """Excel 處理器"""

    @staticmethod
    def read_excel(file_path: Path) -> pd.DataFrame:
        """讀取 Excel 文件"""
        logger.info(f"讀取 Excel: {file_path}")
        df = pd.read_excel(file_path)
        logger.info(f"讀取 {len(df)} 行數據")
        return df

    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """數據清洗"""
        logger.info("開始數據清洗")

        # 刪除重複行
        original_len = len(df)
        df = df.drop_duplicates()
        logger.info(f"刪除 {original_len - len(df)} 行重複數據")

        # 填充缺失值
        df = df.fillna(0)

        # 移除空白
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip()

        logger.info("數據清洗完成")
        return df

    @staticmethod
    def transform_data(df: pd.DataFrame) -> pd.DataFrame:
        """數據轉換"""
        logger.info("開始數據轉換")

        # 範例：添加計算列
        if 'quantity' in df.columns and 'price' in df.columns:
            df['total'] = df['quantity'] * df['price']
            logger.info("添加計算列: total")

        # 範例：格式化日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            logger.info("格式化日期列")

        return df

    @staticmethod
    def generate_report(df: pd.DataFrame, output_path: Path):
        """生成報表"""
        logger.info(f"生成報表: {output_path}")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 原始數據
            df.to_excel(writer, sheet_name='Data', index=False)

            # 統計摘要
            if 'total' in df.columns:
                summary = pd.DataFrame({
                    '指標': ['總計', '平均', '最大', '最小'],
                    '金額': [
                        df['total'].sum(),
                        df['total'].mean(),
                        df['total'].max(),
                        df['total'].min()
                    ]
                })
                summary.to_excel(writer, sheet_name='Summary', index=False)

        logger.info("報表生成完成")

def demo_excel_processing():
    """示範 Excel 處理"""

    # 創建示例數據
    sample_data = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'product': ['A', 'B', 'C'],
        'quantity': [10, 20, 30],
        'price': [100, 200, 300]
    })

    # 保存示例文件
    input_file = INPUT_DIR / "sample_data.xlsx"
    sample_data.to_excel(input_file, index=False)
    logger.info(f"創建示例文件: {input_file}")

    # 處理流程
    processor = ExcelProcessor()

    # 1. 讀取
    df = processor.read_excel(input_file)

    # 2. 清洗
    df = processor.clean_data(df)

    # 3. 轉換
    df = processor.transform_data(df)

    # 4. 生成報表
    output_file = OUTPUT_DIR / "processed_report.xlsx"
    processor.generate_report(df, output_file)

    print(f"\n處理完成！報表已保存到: {output_file}")

if __name__ == "__main__":
    demo_excel_processing()
```

### PDF 處理

```python
import pdfplumber
from pathlib import Path

def extract_pdf_text(pdf_path: Path) -> str:
    """提取 PDF 文字"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_pdf_tables(pdf_path: Path) -> list:
    """提取 PDF 表格"""
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for page in pdf.pages:
            page_tables = page.extract_tables()
            tables.extend(page_tables)
    return tables
```

---

## 實戰專案：網頁數據採集

### 專案目標

創建一個自動化腳本，從電商網站採集產品資訊並保存到 Excel。

### 完整實現

**scripts/ecommerce_scraper.py**

```python
"""
電商數據採集器
功能：自動採集產品資訊並保存到 Excel
"""
from playwright.sync_api import sync_playwright, Page
import pandas as pd
from typing import List, Dict
from utils.logger import setup_logger
from config.settings import OUTPUT_DIR
import time

logger = setup_logger("ecommerce_scraper")

class EcommerceScraper:
    """電商採集器"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.products: List[Dict] = []

    def scrape(self, url: str, max_products: int = 20):
        """
        採集產品資訊

        Args:
            url: 目標網址
            max_products: 最大採集數量
        """
        logger.info(f"開始採集: {url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            try:
                # 訪問頁面
                page.goto(url, wait_until='networkidle')
                logger.info("頁面載入完成")

                # 等待產品列表載入
                page.wait_for_selector('.product-item', timeout=10000)

                # 滾動頁面以載入更多產品
                self._scroll_page(page)

                # 提取產品資訊
                self._extract_products(page, max_products)

                logger.info(f"採集完成，共 {len(self.products)} 個產品")

            except Exception as e:
                logger.error(f"採集錯誤: {str(e)}", exc_info=True)
                page.screenshot(path=OUTPUT_DIR / "error_screenshot.png")
                raise

            finally:
                browser.close()

    def _scroll_page(self, page: Page, scrolls: int = 3):
        """滾動頁面以載入動態內容"""
        for i in range(scrolls):
            page.evaluate('window.scrollBy(0, window.innerHeight)')
            time.sleep(1)
            logger.info(f"滾動頁面 {i+1}/{scrolls}")

    def _extract_products(self, page: Page, max_products: int):
        """提取產品資訊"""
        product_items = page.locator('.product-item')
        count = min(product_items.count(), max_products)

        logger.info(f"找到 {product_items.count()} 個產品，提取前 {count} 個")

        for i in range(count):
            try:
                item = product_items.nth(i)

                # 提取資訊（選擇器需根據實際網站調整）
                product = {
                    'title': self._safe_extract(item, '.product-title'),
                    'price': self._safe_extract(item, '.product-price'),
                    'rating': self._safe_extract(item, '.product-rating'),
                    'link': self._safe_extract_attr(item, 'a', 'href'),
                }

                self.products.append(product)
                logger.info(f"提取產品 {i+1}: {product['title']}")

            except Exception as e:
                logger.warning(f"提取產品 {i+1} 時出錯: {str(e)}")
                continue

    def _safe_extract(self, element, selector: str, default: str = "N/A") -> str:
        """安全提取文字"""
        try:
            elem = element.locator(selector).first
            return elem.inner_text() if elem.count() > 0 else default
        except:
            return default

    def _safe_extract_attr(self, element, selector: str, attr: str, default: str = "N/A") -> str:
        """安全提取屬性"""
        try:
            elem = element.locator(selector).first
            return elem.get_attribute(attr) if elem.count() > 0 else default
        except:
            return default

    def save_to_excel(self, filename: str = "products.xlsx"):
        """保存到 Excel"""
        if not self.products:
            logger.warning("沒有數據可保存")
            return

        df = pd.DataFrame(self.products)
        output_path = OUTPUT_DIR / filename

        df.to_excel(output_path, index=False)
        logger.info(f"數據已保存到: {output_path}")

        # 輸出統計
        print(f"\n採集統計:")
        print(f"總產品數: {len(self.products)}")
        print(f"保存位置: {output_path}")

def main():
    """主函數"""
    # 示例：採集書籍資訊（需替換為實際網址）
    scraper = EcommerceScraper(headless=False)

    # 注意：請替換為合法的測試網址
    # 許多網站禁止爬蟲，請遵守 robots.txt 和使用條款
    test_url = "https://books.toscrape.com/"  # 練習用網站

    scraper.scrape(test_url, max_products=20)
    scraper.save_to_excel("books_data.xlsx")

if __name__ == "__main__":
    main()
```

### 執行與測試

```bash
# 執行採集腳本
python scripts/ecommerce_scraper.py

# 檢查結果
ls data/output/
```

---

## 總結與下一步

### 本章學習重點

✅ 環境配置與專案結構
✅ 基礎自動化腳本開發
✅ 瀏覽器自動化（Playwright/Selenium）
✅ 桌面應用自動化（PyAutoGUI）
✅ 資料處理（Pandas、Excel、PDF）
✅ 完整的實戰專案實現

### 最佳實踐

1. **始終使用日誌記錄**：便於調試和追蹤
2. **錯誤處理**：使用 try-except 處理異常
3. **等待策略**：避免因載入延遲導致的失敗
4. **截圖保存**：錯誤時保存截圖便於分析
5. **遵守規範**：尊重 robots.txt 和網站使用條款

### 常見問題

**Q: 元素找不到怎麼辦？**
A: 檢查選擇器是否正確，增加等待時間，使用 `page.screenshot()` 確認頁面狀態。

**Q: 如何處理動態內容？**
A: 使用 `wait_for_selector()` 等待元素出現，或 `wait_for_load_state('networkidle')` 等待網路閒置。

**Q: 如何避免被網站封鎖？**
A: 添加隨機延遲，設置 User-Agent，使用代理，降低請求頻率。

### 下一步

繼續學習 [tutorial-part2-llm-integration.md](./tutorial-part2-llm-integration.md)，將 LLM 整合到 RPA 流程中，實現智能化自動化！

---

## 練習作業

1. **基礎練習**：修改 Hello RPA 腳本，讓它打開你電腦上的任意應用程式
2. **中級練習**：創建一個腳本自動登入你常用的網站（測試帳號）
3. **進階練習**：實現一個自動化腳本，每天定時採集新聞標題並發送郵件報告

完成作業後，查看 [examples/](./examples/) 目錄中的參考解答。
