
設定以及執行得過程
--------------
Prerequisites

Python 3.9+

Google Gemini API key (or choose other LLM 
providers like OpenAI or Groq).

Google APIs credentials.
API keys for integrated tools (RapidAPI, Serper API).

API keys and configurations for your chosen 

CRM (check .env.example for more information).

Necessary Python libraries (listed in requirements.txt).

--------------

先執行 python setup_script.py

然後進入虛擬環境 source venv/bin/activate 

因為目前的版本需要安裝 html2text

進行安裝 pip install html2text

然後 cd sales-outreach-automation-langgraph

修改.env 根據下面的api key 修改您自己的 key，可順便參考原項目的readme.md

--------------

#### Gemini API Key
GEMINI_API_KEY="gemini-api-key"
GOOGLE_API_KEY="gemini-api-key"

#### OpenAI API KEY
OPENAI_API_KEY="gemini-api-key"

#### Serper API Key for using Serper search
SERPER_API_KEY="serper-api-key"

#### RapidAPI Key for accessing Linkedin scraper API
RAPIDAPI_KEY="rapid-api-key"

#### Airtable API configurations:
#### AIRTABLE_ACCESS_TOKEN: Access token for accessing Airtable
#### AIRTABLE_BASE_ID: The ID of the Airtable base you're working with
#### AIRTABLE_TABLE_NAME: The name of the table within the base
AIRTABLE_ACCESS_TOKEN=""
AIRTABLE_BASE_ID=airtable-base-id
AIRTABLE_TABLE_NAME=table-name

#### HubSpot API Key for connecting to HubSpot services
#### Replace with your actual HubSpot private app token (PAT).
HUBSPOT_API_KEY=""

#### Google Sheet configuration:
#### SHEET_ID: Google sheet id extracted from its URL
SHEET_ID=""

--------------

接著是設定 credentials.json

以下是如何申請、設定 Google API 憑證並生成 credentials.json 檔案的步驟：

先到 https://developers.google.com/gmail/api/quickstart/python?hl=zh-tw

根據 授權電腦版應用程式的憑證 這邊的步驟執行

然後把下載的 credentials.json 移動到 sales-outreach-automation-langgraph 下面跟main.py 同級的目錄

然後在 https://console.cloud.google.com/auth/clients?hl=zh-tw 到API了和服務

點擊 OAuth同意畫面 -> 資料存取權 ->新增或移除範圍 -> Gemini gmail相關的請詳細檢查確定有用到就點擊勾勾

--------------

AIRTABLE_ACCESS_TOKEN=""

AIRTABLE_BASE_ID=airtable-base-id

AIRTABLE_TABLE_NAME=table-name

**如何取得這些值：**

*   **`AIRTABLE_ACCESS_TOKEN` (Personal Access Token):**
    1.  登入您的 Airtable 帳戶。
    2.  前往 [Airtable Developer Hub](https://airtable.com/create/tokens)
    3.  點擊 "Create token."
    4.  輸入token的名稱
    5. 點擊 "+ Add a scope"，然後選擇您需要的權限，例如：
       *   `data.records:read`: 讀取資料。
       *   `data.records:write`: 寫入資料 (包括建立、更新、刪除)。
       *   `schema.bases:read`: 讀取 Base 的結構 (例如表格名稱、欄位類型)。
    6. 點擊 "+ Add a base"，選擇要授權的特定 Base，或選擇 "All current and future bases in all current and future workspaces" 以授權所有 Base。
    7. 點擊 "Create token."
    8.  複製產生的 Personal Access Token。**請妥善保管，不要分享給他人。**
*   **`AIRTABLE_BASE_ID`:**
    1.  開啟您的 Airtable Base。
    2.  Base ID 會在網址中，格式為 `appXXXXXXXXXXXXXX`。例如：`https://airtable.com/appXXXXXXXXXXXXXX/tblYYYYYYYYYYYYYY` 中的 `appXXXXXXXXXXXXXX` 就是 Base ID。
    3.  您也可以在 Airtable API 文件中找到 Base ID。
*   **`AIRTABLE_TABLE_NAME`:**
    *   就是您在 Airtable Base 中建立的表格名稱。 預設(沒修改的話)是 “Databases”
然後記得在table最右邊一欄增加一個status的欄位，否則執行時會出錯。

----------

最後記得執行 python main.py
