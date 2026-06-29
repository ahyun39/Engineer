# Claude MCP × Google Spreadsheets 자동화

> Google API 키, OAuth 없이 — Apps Script 하나로 스프레드시트를 Claude와 연결

**[인터랙티브 가이드 보기](https://ahyun39.github.io/Engineer/Engineer/blob/main/Projects/mcp_google_spreadsheets/mcp-google-spreadsheets-guide.html)**

---

## 전체 구조

```
Claude (Desktop/CLI)
    ↓ stdio (MCP)
Node.js MCP 서버 (server.js)
    ↓ HTTP POST
Google Apps Script Web App (doPost)
    ↓ Sheets API
Google Spreadsheet
```

## 빠른 시작 (4단계)

### 1. Google Apps Script 웹 앱 만들기

스프레드시트 → **확장 프로그램 → Apps Script** → 아래 코드 붙여넣기 → **배포 → 새 배포 → 웹 앱**으로 배포

- 실행 계정: **나**
- 액세스: **모든 사용자**

배포 후 나타나는 **웹 앱 URL**을 복사해 두세요.

보안 설정 (권장): GAS 편집기 **⚙️ → 스크립트 속성**에서 두 값 추가

| 속성 | 값 |
|---|---|
| `MCP_SECRET` | `openssl rand -hex 16` 으로 생성한 랜덤 문자열 |
| `ALLOWED_IDS` | 허가할 스프레드시트 ID (여러 개면 쉼표 구분) |

### 2. 프로젝트 초기화

```bash
mkdir claude-gas-mcp && cd claude-gas-mcp
mkdir src config
npm init -y
npm install @modelcontextprotocol/sdk axios
```

`config/mcp-config.json`

```json
{
  "name": "Google Apps Script MCP Server",
  "version": "1.0.0",
  "config": {
    "webAppUrl": "YOUR_WEB_APP_URL",
    "testSpreadsheetId": "YOUR_SPREADSHEET_ID"
  },
  "tools": ["read_google_sheet", "write_google_sheet"]
}
```

### 3. MCP 서버 코드

`src/server.js` → [전체 코드는 가이드 참고](https://ahyun39.github.io/ML-Engineer/Projects/mcp_google_spreadsheets/mcp-google-spreadsheets-guide.html#step3)

핵심 구조: `ListToolsRequestSchema` 핸들러로 도구 목록 제공 → `CallToolRequestSchema` 핸들러로 GAS 웹 앱에 HTTP POST 전달

### 4. Claude Desktop에 등록

`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-apps-script-mcp": {
      "command": "node",
      "args": ["/절대경로/claude-gas-mcp/src/server.js"],
      "env": {
        "GAS_WEB_APP_URL": "YOUR_WEB_APP_URL",
        "MCP_SECRET": "YOUR_SECRET_KEY"
      }
    }
  }
}
```

저장 후 **Claude Desktop 재시작** → 채팅창 `+` → `커넥터`에서 `google-apps-script-mcp` 확인

---

## 사용 예시

```
"스프레드시트 ID=abc123 의 A1:D10 읽어줘"
"B2:C4에 [[1,2],[3,4],[5,6]] 써줘"
```

## 보안 주의사항

| 항목 | 주의 |
|---|---|
| 웹 앱 URL | 소스/config 파일에 직접 기록하지 않고 환경변수로만 관리 |
| MCP_SECRET | GAS 스크립트 속성과 claude_desktop_config.json env에 동일하게 설정 |
| ALLOWED_IDS | 접근 허가할 스프레드시트 ID만 화이트리스트로 등록 |

## 핵심 요약

- **API 키 불필요** — GAS 웹 앱 URL 하나로 연결
- **핸들러 2개** — `ListTools` + `CallTool` 만으로 Claude가 도구 자동 인식
- **자연어 제어** — "A1:D5 읽어줘" 한 문장으로 스프레드시트 조작
