import sys
import os
import csv
import shutil
import sqlite3
from datetime import datetime, date

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox, QDateEdit,
    QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QDialog, QFileDialog, QHeaderView,
    QSpinBox, QGroupBox, QAbstractItemView, QTextBrowser
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from matplotlib import font_manager, rcParams


APP_NAME = "MoneyFlow"
def setup_japanese_font():
    candidates = [
        "Yu Gothic",
        "Yu Gothic UI",
        "Meiryo",
        "MS Gothic",
        "Noto Sans CJK JP",
        "IPAexGothic",
    ]

    available_fonts = {f.name for f in font_manager.fontManager.ttflist}

    for font_name in candidates:
        if font_name in available_fonts:
            rcParams["font.family"] = font_name
            break

    rcParams["axes.unicode_minus"] = False

DB_FILE = "moneyflow.db"


STYLE = """
QMainWindow {
    background-color: #101418;
}

QWidget {
    color: #EAEFF4;
    font-family: "Yu Gothic UI", "Meiryo", sans-serif;
    font-size: 14px;
}

QTabWidget::pane {
    border: 1px solid #26313A;
    border-radius: 12px;
    background: #151A20;
}

QTabBar::tab {
    background: #1B222A;
    color: #AEB8C2;
    padding: 10px 18px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background: #2F80ED;
    color: white;
}

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {
    background-color: #1B222A;
    border: 1px solid #303C47;
    border-radius: 8px;
    padding: 7px;
    color: #F3F7FA;
}

QPushButton {
    background-color: #2F80ED;
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 14px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4493FF;
}

QPushButton:pressed {
    background-color: #1F6FD6;
}

QPushButton#danger {
    background-color: #EB5757;
}

QPushButton#danger:hover {
    background-color: #FF6B6B;
}

QPushButton#subtle {
    background-color: #26313A;
    color: #EAEFF4;
}

QTableWidget {
    background-color: #151A20;
    alternate-background-color: #1A2027;
    gridline-color: #26313A;
    border: 1px solid #26313A;
    border-radius: 10px;
}

QHeaderView::section {
    background-color: #202832;
    color: #DCE6EF;
    padding: 8px;
    border: none;
    font-weight: bold;
}

QGroupBox {
    border: 1px solid #26313A;
    border-radius: 12px;
    margin-top: 14px;
    padding: 12px;
    background-color: #151A20;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #8AB4F8;
    font-weight: bold;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #2F80ED;
    color: white;
}

QMenuBar {
    background-color: #101418;
    color: #EAEFF4;
    padding: 6px;
}

QMenuBar::item:selected {
    background-color: #26313A;
    border-radius: 6px;
}

QMenu {
    background-color: #151A20;
    color: #EAEFF4;
    border: 1px solid #26313A;
}

QMenu::item:selected {
    background-color: #2F80ED;
}

QScrollBar:vertical {
    background: #101418;
    width: 12px;
}

QScrollBar::handle:vertical {
    background: #303C47;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #4A5A68;
}
"""

HELP_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<style>
    body {
        background-color: #101418;
        color: #EAEFF4;
        font-family: "Yu Gothic UI", "Meiryo", sans-serif;
        line-height: 1.8;
        margin: 0;
        padding: 24px;
    }

    h1 {
        color: #FFFFFF;
        font-size: 28px;
        border-bottom: 2px solid #2F80ED;
        padding-bottom: 8px;
    }

    h2 {
        color: #8AB4F8;
        font-size: 21px;
        margin-top: 28px;
        border-left: 5px solid #2F80ED;
        padding-left: 10px;
    }

    h3 {
        color: #FFFFFF;
        font-size: 17px;
        margin-top: 20px;
    }

    p {
        color: #DCE6EF;
    }

    ul {
        margin-top: 6px;
        margin-bottom: 14px;
    }

    li {
        margin-bottom: 6px;
    }

    .card {
        background-color: #151A20;
        border: 1px solid #26313A;
        border-radius: 14px;
        padding: 16px;
        margin: 14px 0;
    }

    .point {
        color: #27AE60;
        font-weight: bold;
    }

    .warn {
        color: #F2C94C;
        font-weight: bold;
    }

    .danger {
        color: #EB5757;
        font-weight: bold;
    }

    .kbd {
        background-color: #26313A;
        border: 1px solid #3A4652;
        border-radius: 6px;
        padding: 2px 7px;
        color: #FFFFFF;
        font-weight: bold;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 18px;
    }

    th {
        background-color: #202832;
        color: #FFFFFF;
        padding: 10px;
        text-align: left;
    }

    td {
        border: 1px solid #303C47;
        padding: 10px;
        color: #DCE6EF;
    }

    code {
        background-color: #1B222A;
        color: #8AB4F8;
        padding: 2px 5px;
        border-radius: 5px;
    }
</style>
</head>
<body>

<h1>MoneyFlow 使い方ガイド</h1>

<div class="card">
    <p>
        <b>MoneyFlow</b> は、銀行口座、PayPay、現金、クレジットカード、投資資産をまとめて管理できる家計簿アプリです。
    </p>
    <p>
        目的は、<span class="point">今いくら持っているか</span>、
        <span class="point">何に使ったか</span>、
        <span class="point">資産がどう増減しているか</span>を見やすく確認することです。
    </p>
</div>

<h2>1. ダッシュボード</h2>

<p>アプリを開いたときに、全体の資産状況を確認できます。</p>

<table>
<tr>
    <th>項目</th>
    <th>意味</th>
</tr>
<tr>
    <td>総資産</td>
    <td>口座・PayPay・現金 + 投資評価額 - クレカ利用額</td>
</tr>
<tr>
    <td>口座・PayPay残高</td>
    <td>登録している銀行口座、PayPay、現金などの合計です。</td>
</tr>
<tr>
    <td>投資評価額</td>
    <td>登録した投資資産の現在評価額の合計です。</td>
</tr>
<tr>
    <td>クレカ利用額</td>
    <td>クレジットカードの未払い利用額です。総資産から差し引かれます。</td>
</tr>
<tr>
    <td>今月収入 / 今月支出</td>
    <td>今月登録した収入と支出の合計です。</td>
</tr>
</table>

<h2>2. 資産管理</h2>

<p>銀行口座、PayPay、現金、クレジットカード、投資資産を登録・編集できます。</p>

<h3>口座 / PayPay / 現金を追加する</h3>
<ul>
    <li>「名前」に銀行名やPayPayなどを入力します。</li>
    <li>「種類」から <code>銀行口座</code>、<code>PayPay</code>、<code>現金</code> を選びます。</li>
    <li>「残高」に現在の金額を入力します。</li>
    <li><span class="kbd">追加</span> ボタンを押すと登録されます。</li>
</ul>

<h3>クレジットカードを追加する</h3>
<ul>
    <li>カード名を入力します。</li>
    <li>現在の利用額を入力します。</li>
    <li>締日と支払日を設定します。</li>
    <li>クレカ利用額は総資産から差し引かれます。</li>
</ul>

<h3>投資資産を追加する</h3>
<ul>
    <li>銘柄名を入力します。</li>
    <li>NISA、iDeCo、株式、投資信託などの種類を選びます。</li>
    <li>数量、取得金額、現在評価額を入力します。</li>
    <li>取得金額と評価額から損益が計算されます。</li>
</ul>

<h3>資産を編集する</h3>
<ul>
    <li>資産一覧から編集したい行を選択します。</li>
    <li><span class="kbd">選択した資産を編集</span> を押します。</li>
    <li>または、資産一覧の行をダブルクリックします。</li>
    <li>内容を修正して保存すると、ダッシュボードにも反映されます。</li>
</ul>

<h3>資産を削除する</h3>
<ul>
    <li>資産一覧から削除したい行を選択します。</li>
    <li><span class="kbd">選択した資産を削除</span> を押します。</li>
    <li><span class="warn">削除すると元に戻せないため注意してください。</span></li>
</ul>

<h2>3. 収支管理</h2>

<p>日々の支出、収入、振替を登録できます。</p>

<table>
<tr>
    <th>種類</th>
    <th>使い方</th>
</tr>
<tr>
    <td>支出</td>
    <td>食費、交通費、娯楽費など、お金を使ったときに登録します。</td>
</tr>
<tr>
    <td>入金</td>
    <td>給与、副業、配当金、臨時収入などを登録します。</td>
</tr>
<tr>
    <td>振替</td>
    <td>銀行口座からPayPayへチャージするなど、資産間の移動に使います。</td>
</tr>
</table>

<div class="card">
    <p>
        <span class="point">ポイント:</span>
        銀行口座からPayPayへ移しただけの場合は「支出」ではなく「振替」として登録してください。
    </p>
</div>

<h2>4. 分析</h2>

<p>分析画面では、登録したデータをグラフで確認できます。</p>

<ul>
    <li>今月の支出割合</li>
    <li>資産構成</li>
    <li>月別収支差額</li>
</ul>

<p>
    支出カテゴリを丁寧に分けて登録すると、何にお金を使っているかが分かりやすくなります。
</p>

<h2>5. 設定</h2>

<h3>カテゴリ追加</h3>
<ul>
    <li>支出、収入、振替のカテゴリを追加できます。</li>
    <li>例: カフェ、日用品、ガソリン、配当金など。</li>
</ul>

<h3>月間予算</h3>
<ul>
    <li>食費や娯楽費など、カテゴリごとに月間予算を設定できます。</li>
    <li>今後、予算進捗バーを追加するとさらに見やすくなります。</li>
</ul>

<h2>6. CSV入出力</h2>

<p>メニューの <span class="kbd">ファイル</span> からCSVを操作できます。</p>

<ul>
    <li><b>取引CSVエクスポート:</b> 登録済みの取引をCSVとして保存します。</li>
    <li><b>取引CSVインポート:</b> CSVから取引を読み込みます。</li>
</ul>

<h2>7. バックアップ</h2>

<p>
    メニューの <span class="kbd">ファイル</span> → <span class="kbd">バックアップ作成</span> から、
    現在のデータベースをバックアップできます。
</p>

<div class="card">
    <p>
        <span class="warn">おすすめ:</span>
        大きく編集する前や、CSVインポート前にはバックアップを作成してください。
    </p>
</div>

<h2>8. よくある使い方</h2>

<h3>PayPayにチャージした場合</h3>
<ul>
    <li>種類は <code>振替</code> を選びます。</li>
    <li>振替元に銀行口座を選びます。</li>
    <li>振替先にPayPayを選びます。</li>
    <li>これは支出ではなく、資産の移動として扱います。</li>
</ul>

<h3>クレジットカードで買い物した場合</h3>
<ul>
    <li>種類は <code>支出</code> を選びます。</li>
    <li>支払元にクレジットカードを選びます。</li>
    <li>クレカ利用額が増え、総資産から差し引かれます。</li>
</ul>

<h3>給料が入った場合</h3>
<ul>
    <li>種類は <code>入金</code> を選びます。</li>
    <li>カテゴリは <code>給与</code> を選びます。</li>
    <li>入金先の銀行口座を選びます。</li>
</ul>

<h2>9. 注意事項</h2>

<ul>
    <li>このアプリはローカルのSQLiteデータベースに保存します。</li>
    <li>データファイルは <code>moneyflow.db</code> です。</li>
    <li>アプリを移動するときは、Pythonファイルと一緒に <code>moneyflow.db</code> も保管してください。</li>
    <li>削除操作は元に戻せないため、必要に応じてバックアップしてください。</li>
</ul>

</body>
</html>
"""

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MoneyFlow ヘルプ")
        self.resize(900, 720)

        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(HELP_HTML)

        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #101418;
                color: #EAEFF4;
                border: 1px solid #26313A;
                border-radius: 12px;
                padding: 8px;
            }
        """)

        close_btn = QPushButton("閉じる")
        close_btn.setObjectName("subtle")
        close_btn.clicked.connect(self.accept)

        layout.addWidget(browser)
        layout.addWidget(close_btn)

def money(value):
    return f"{int(value):,} 円"


class Database:
    def __init__(self, path=DB_FILE):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed()

    def execute(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def fetchall(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def fetchone(self, sql, params=()):
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()

    def create_tables(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                note TEXT,
                created_at TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS credit_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                used_amount REAL NOT NULL DEFAULT 0,
                closing_day INTEGER DEFAULT 25,
                payment_day INTEGER DEFAULT 27,
                note TEXT,
                created_at TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                quantity REAL NOT NULL DEFAULT 0,
                cost REAL NOT NULL DEFAULT 0,
                current_value REAL NOT NULL DEFAULT 0,
                note TEXT,
                created_at TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                memo TEXT,
                from_kind TEXT,
                from_id INTEGER,
                to_kind TEXT,
                to_id INTEGER,
                created_at TEXT NOT NULL
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL UNIQUE,
                monthly_limit REAL NOT NULL DEFAULT 0
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS recurring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                day INTEGER NOT NULL DEFAULT 1,
                account_id INTEGER,
                memo TEXT
            )
        """)

    def seed(self):
        defaults = [
            ("食費", "expense"), ("交通費", "expense"), ("娯楽", "expense"),
            ("医療", "expense"), ("サブスク", "expense"), ("通信費", "expense"),
            ("家賃", "expense"), ("光熱費", "expense"), ("雑費", "expense"),
            ("給与", "income"), ("賞与", "income"), ("副業", "income"),
            ("配当金", "income"), ("売却益", "income"), ("臨時収入", "income"),
            ("振替", "transfer")
        ]
        for name, typ in defaults:
            try:
                self.execute(
                    "INSERT INTO categories(name, type) VALUES (?, ?)",
                    (name, typ)
                )
            except sqlite3.IntegrityError:
                pass

    def update_account_balance(self, account_id, delta):
        self.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (delta, account_id)
        )

    def update_card_used(self, card_id, delta):
        self.execute(
            "UPDATE credit_cards SET used_amount = used_amount + ? WHERE id = ?",
            (delta, card_id)
        )

    def apply_transaction_effect(self, tx, sign=1):
        amount = float(tx["amount"]) * sign
        typ = tx["type"]

        if typ == "expense":
            if tx["from_kind"] == "account" and tx["from_id"]:
                self.update_account_balance(tx["from_id"], -amount)
            elif tx["from_kind"] == "card" and tx["from_id"]:
                self.update_card_used(tx["from_id"], amount)

        elif typ == "income":
            if tx["to_kind"] == "account" and tx["to_id"]:
                self.update_account_balance(tx["to_id"], amount)

        elif typ == "transfer":
            if tx["from_kind"] == "account" and tx["from_id"]:
                self.update_account_balance(tx["from_id"], -amount)
            if tx["to_kind"] == "account" and tx["to_id"]:
                self.update_account_balance(tx["to_id"], amount)


class MoneyFlowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 820)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = DashboardTab(self.db)
        self.assets_tab = AssetsTab(self.db, self.refresh_all)
        self.transaction_tab = TransactionTab(self.db, self.refresh_all)
        self.analysis_tab = AnalysisTab(self.db)
        self.settings_tab = SettingsTab(self.db, self.refresh_all)

        self.tabs.addTab(self.dashboard_tab, "ダッシュボード")
        self.tabs.addTab(self.assets_tab, "資産管理")
        self.tabs.addTab(self.transaction_tab, "収支管理")
        self.tabs.addTab(self.analysis_tab, "分析")
        self.tabs.addTab(self.settings_tab, "設定")

        self.create_menu()
        self.refresh_all()

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("ファイル")

        backup_action = QAction("バックアップ作成", self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)

        export_action = QAction("取引CSVエクスポート", self)
        export_action.triggered.connect(self.export_transactions_csv)
        file_menu.addAction(export_action)

        import_action = QAction("取引CSVインポート", self)
        import_action.triggered.connect(self.import_transactions_csv)
        file_menu.addAction(import_action)

        help_menu = menu.addMenu("ヘルプ")

        usage_action = QAction("使い方", self)
        usage_action.triggered.connect(self.show_help)
        help_menu.addAction(usage_action)

    def show_help(self):
        dlg = HelpDialog()
        dlg.exec()

    def refresh_all(self):
        self.dashboard_tab.refresh()
        self.assets_tab.refresh()
        self.transaction_tab.refresh()
        self.analysis_tab.refresh()
        self.settings_tab.refresh()

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.db"
        shutil.copyfile(DB_FILE, filename)
        QMessageBox.information(self, "バックアップ完了", f"{filename} を作成しました。")

    def export_transactions_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "CSV保存", "transactions.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        rows = self.db.fetchall("SELECT * FROM transactions ORDER BY date DESC, id DESC")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "date", "type", "amount", "category", "memo",
                "from_kind", "from_id", "to_kind", "to_id", "created_at"
            ])
            for r in rows:
                writer.writerow([
                    r["id"], r["date"], r["type"], r["amount"], r["category"], r["memo"],
                    r["from_kind"], r["from_id"], r["to_kind"], r["to_id"], r["created_at"]
                ])

        QMessageBox.information(self, "完了", "CSVを書き出しました。")

    def import_transactions_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "CSV読み込み", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        imported = 0
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tx = {
                    "date": row.get("date") or date.today().isoformat(),
                    "type": row.get("type") or "expense",
                    "amount": float(row.get("amount") or 0),
                    "category": row.get("category"),
                    "memo": row.get("memo"),
                    "from_kind": row.get("from_kind"),
                    "from_id": int(row["from_id"]) if row.get("from_id") else None,
                    "to_kind": row.get("to_kind"),
                    "to_id": int(row["to_id"]) if row.get("to_id") else None,
                    "created_at": datetime.now().isoformat()
                }

                cur = self.db.execute("""
                    INSERT INTO transactions
                    (date, type, amount, category, memo, from_kind, from_id, to_kind, to_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx["date"], tx["type"], tx["amount"], tx["category"], tx["memo"],
                    tx["from_kind"], tx["from_id"], tx["to_kind"], tx["to_id"], tx["created_at"]
                ))

                tx["id"] = cur.lastrowid
                self.db.apply_transaction_effect(tx, sign=1)
                imported += 1

        self.refresh_all()
        QMessageBox.information(self, "完了", f"{imported} 件読み込みました。")


class DashboardTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout(self)
        title = QLabel("MoneyFlow ダッシュボード")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        self.card_grid = QGridLayout()
        layout.addLayout(self.card_grid)

        self.summary_labels = {}
        items = [
            ("total_assets", "総資産"),
            ("cash", "口座・PayPay残高"),
            ("investments", "投資評価額"),
            ("cards", "クレカ利用額"),
            ("month_income", "今月収入"),
            ("month_expense", "今月支出"),
            ("month_balance", "今月収支"),
            ("profit", "投資損益")
        ]

        for i, (key, name) in enumerate(items):
            box = self.create_card(name)
            self.summary_labels[key] = box.findChild(QLabel, "value")
            self.card_grid.addWidget(box, i // 4, i % 4)

        self.figure = Figure(figsize=(9, 4), facecolor="#151A20")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def create_card(self, title):
        box = QGroupBox()
        box.setStyleSheet("""
            QGroupBox {
                background-color: #151A20;
                border: 1px solid #26313A;
                border-radius: 18px;
            }
        """)
        layout = QVBoxLayout(box)
        t = QLabel(title)
        t.setStyleSheet("color: #AEB8C2; font-weight: bold;")
        v = QLabel("0 円")
        v.setObjectName("value")
        v.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(t)
        layout.addWidget(v)
        return box

    def refresh(self):
        accounts = self.db.fetchall("SELECT COALESCE(SUM(balance), 0) AS total FROM accounts")
        inv = self.db.fetchall("SELECT COALESCE(SUM(current_value), 0) AS total, COALESCE(SUM(cost), 0) AS cost FROM investments")
        cards = self.db.fetchall("SELECT COALESCE(SUM(used_amount), 0) AS total FROM credit_cards")

        cash = accounts[0]["total"]
        investment_value = inv[0]["total"]
        investment_cost = inv[0]["cost"]
        card_used = cards[0]["total"]

        total_assets = cash + investment_value - card_used
        profit = investment_value - investment_cost

        month = date.today().strftime("%Y-%m")
        income = self.db.fetchone("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE type = 'income' AND substr(date, 1, 7) = ?
        """, (month,))["total"]

        expense = self.db.fetchone("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE type = 'expense' AND substr(date, 1, 7) = ?
        """, (month,))["total"]

        values = {
            "total_assets": total_assets,
            "cash": cash,
            "investments": investment_value,
            "cards": card_used,
            "month_income": income,
            "month_expense": expense,
            "month_balance": income - expense,
            "profit": profit
        }

        for k, v in values.items():
            self.summary_labels[k].setText(money(v))

        self.draw_monthly_chart()

    def draw_monthly_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#151A20")

        rows = self.db.fetchall("""
            SELECT substr(date, 1, 7) AS ym,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
            FROM transactions
            GROUP BY ym
            ORDER BY ym
            LIMIT 12
        """)

        months = [r["ym"] for r in rows]
        incomes = [r["income"] for r in rows]
        expenses = [r["expense"] for r in rows]

        if not rows:
            ax.text(0.5, 0.5, "まだ取引データがありません", color="white",
                    ha="center", va="center", transform=ax.transAxes)
        else:
            x = range(len(months))
            ax.bar([i - 0.2 for i in x], incomes, width=0.4, label="収入")
            ax.bar([i + 0.2 for i in x], expenses, width=0.4, label="支出")
            ax.set_xticks(list(x))
            ax.set_xticklabels(months, rotation=30, color="white")
            ax.legend()

        ax.set_title("月別収支", color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#303C47")
        self.canvas.draw()

class AssetEditDialog(QDialog):
    def __init__(self, db, asset_kind, asset_id):
        super().__init__()
        self.db = db
        self.asset_kind = asset_kind
        self.asset_id = asset_id

        self.setWindowTitle("資産を編集")
        self.resize(460, 520)

        self.layout = QVBoxLayout(self)

        title = QLabel("資産編集")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
        self.layout.addWidget(title)

        self.name = QLineEdit()
        self.kind = QComboBox()

        self.balance = QDoubleSpinBox()
        self.balance.setMaximum(999999999)
        self.balance.setMinimum(-999999999)
        self.balance.setSuffix(" 円")

        self.used_amount = QDoubleSpinBox()
        self.used_amount.setMaximum(999999999)
        self.used_amount.setMinimum(0)
        self.used_amount.setSuffix(" 円")

        self.closing_day = QSpinBox()
        self.closing_day.setRange(1, 31)

        self.payment_day = QSpinBox()
        self.payment_day.setRange(1, 31)

        self.quantity = QDoubleSpinBox()
        self.quantity.setMaximum(999999999)
        self.quantity.setDecimals(4)

        self.cost = QDoubleSpinBox()
        self.cost.setMaximum(999999999)
        self.cost.setSuffix(" 円")

        self.current_value = QDoubleSpinBox()
        self.current_value.setMaximum(999999999)
        self.current_value.setSuffix(" 円")

        self.build_form()

        button_row = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save)

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setObjectName("subtle")
        cancel_btn.clicked.connect(self.reject)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        self.layout.addLayout(button_row)

    def add_label_widget(self, label_text, widget):
        label = QLabel(label_text)
        label.setStyleSheet("color: #AEB8C2; font-weight: bold;")
        self.layout.addWidget(label)
        self.layout.addWidget(widget)

    def build_form(self):
        if self.asset_kind == "account":
            row = self.db.fetchone("SELECT * FROM accounts WHERE id = ?", (self.asset_id,))
            self.kind.addItems(["銀行口座", "PayPay", "現金", "その他"])

            self.name.setText(row["name"])
            self.kind.setCurrentText(row["kind"])
            self.balance.setValue(float(row["balance"]))

            self.add_label_widget("名前", self.name)
            self.add_label_widget("種類", self.kind)
            self.add_label_widget("残高", self.balance)

        elif self.asset_kind == "card":
            row = self.db.fetchone("SELECT * FROM credit_cards WHERE id = ?", (self.asset_id,))

            self.name.setText(row["name"])
            self.used_amount.setValue(float(row["used_amount"]))
            self.closing_day.setValue(int(row["closing_day"]))
            self.payment_day.setValue(int(row["payment_day"]))

            self.add_label_widget("カード名", self.name)
            self.add_label_widget("利用額", self.used_amount)
            self.add_label_widget("締日", self.closing_day)
            self.add_label_widget("支払日", self.payment_day)

        elif self.asset_kind == "investment":
            row = self.db.fetchone("SELECT * FROM investments WHERE id = ?", (self.asset_id,))
            self.kind.addItems(["NISA", "iDeCo", "株式", "投資信託", "ETF", "暗号資産", "その他"])

            self.name.setText(row["name"])
            self.kind.setCurrentText(row["kind"])
            self.quantity.setValue(float(row["quantity"]))
            self.cost.setValue(float(row["cost"]))
            self.current_value.setValue(float(row["current_value"]))

            self.add_label_widget("銘柄名", self.name)
            self.add_label_widget("種類", self.kind)
            self.add_label_widget("数量", self.quantity)
            self.add_label_widget("取得金額", self.cost)
            self.add_label_widget("評価額", self.current_value)

    def save(self):
        name = self.name.text().strip()

        if not name:
            QMessageBox.warning(self, "入力エラー", "名前を入力してください。")
            return

        if self.asset_kind == "account":
            self.db.execute("""
                UPDATE accounts
                SET name = ?, kind = ?, balance = ?
                WHERE id = ?
            """, (
                name,
                self.kind.currentText(),
                self.balance.value(),
                self.asset_id
            ))

        elif self.asset_kind == "card":
            self.db.execute("""
                UPDATE credit_cards
                SET name = ?, used_amount = ?, closing_day = ?, payment_day = ?
                WHERE id = ?
            """, (
                name,
                self.used_amount.value(),
                self.closing_day.value(),
                self.payment_day.value(),
                self.asset_id
            ))

        elif self.asset_kind == "investment":
            self.db.execute("""
                UPDATE investments
                SET name = ?, kind = ?, quantity = ?, cost = ?, current_value = ?
                WHERE id = ?
            """, (
                name,
                self.kind.currentText(),
                self.quantity.value(),
                self.cost.value(),
                self.current_value.value(),
                self.asset_id
            ))

        self.accept()

class AssetsTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        title = QLabel("資産管理")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("銀行口座、PayPay、クレジットカード、投資資産を登録・編集できます。")
        subtitle.setObjectName("pageSubTitle")
        layout.addWidget(subtitle)

        self.form_tabs = QTabWidget()
        self.form_tabs.addTab(self.account_form(), "口座 / PayPay / 現金")
        self.form_tabs.addTab(self.card_form(), "クレジットカード")
        self.form_tabs.addTab(self.investment_form(), "投資")
        self.form_tabs.setMaximumHeight(290)
        layout.addWidget(self.form_tabs)

        table_title_row = QHBoxLayout()

        table_title = QLabel("資産一覧")
        table_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")

        table_hint = QLabel("ダブルクリックでも編集できます")
        table_hint.setStyleSheet("color: #94A3B8;")

        table_title_row.addWidget(table_title)
        table_title_row.addStretch()
        table_title_row.addWidget(table_hint)

        layout.addLayout(table_title_row)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.cellDoubleClicked.connect(lambda row, col: self.edit_selected())
        layout.addWidget(self.table, stretch=1)

        btns = QHBoxLayout()
        btns.setSpacing(10)

        edit_btn = QPushButton("選択した資産を編集")
        edit_btn.setObjectName("primaryLarge")
        edit_btn.clicked.connect(self.edit_selected)

        delete_btn = QPushButton("選択した資産を削除")
        delete_btn.setObjectName("dangerLarge")
        delete_btn.clicked.connect(self.delete_selected)

        btns.addWidget(edit_btn)
        btns.addWidget(delete_btn)

        layout.addLayout(btns)
    
    def account_form(self):
        box = QGroupBox("口座 / PayPay / 現金を追加")
        box.setObjectName("formCard")

        layout = QGridLayout(box)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(10)

        self.acc_name = QLineEdit()
        self.acc_name.setPlaceholderText("例: 三井住友銀行 / PayPay")

        self.acc_kind = QComboBox()
        self.acc_kind.addItems(["銀行口座", "PayPay", "現金", "その他"])

        self.acc_balance = QDoubleSpinBox()
        self.acc_balance.setMaximum(999999999)
        self.acc_balance.setSuffix(" 円")

        add_btn = QPushButton("追加")
        add_btn.setObjectName("primaryLarge")
        add_btn.clicked.connect(self.add_account)

        layout.addWidget(QLabel("名前"), 0, 0)
        layout.addWidget(self.acc_name, 1, 0)

        layout.addWidget(QLabel("種類"), 0, 1)
        layout.addWidget(self.acc_kind, 1, 1)

        layout.addWidget(QLabel("残高"), 0, 2)
        layout.addWidget(self.acc_balance, 1, 2)

        layout.addWidget(add_btn, 1, 3)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        layout.setColumnStretch(3, 1)

        return box
    
    def card_form(self):
        box = QGroupBox("クレジットカードを追加")
        box.setObjectName("formCard")

        layout = QGridLayout(box)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(10)

        self.card_name = QLineEdit()
        self.card_name.setPlaceholderText("例: 楽天カード")

        self.card_used = QDoubleSpinBox()
        self.card_used.setMaximum(999999999)
        self.card_used.setSuffix(" 円")

        self.card_closing = QSpinBox()
        self.card_closing.setRange(1, 31)
        self.card_closing.setValue(25)

        self.card_payment = QSpinBox()
        self.card_payment.setRange(1, 31)
        self.card_payment.setValue(27)

        add_btn = QPushButton("追加")
        add_btn.setObjectName("primaryLarge")
        add_btn.clicked.connect(self.add_card)

        layout.addWidget(QLabel("カード名"), 0, 0)
        layout.addWidget(self.card_name, 1, 0)

        layout.addWidget(QLabel("利用額"), 0, 1)
        layout.addWidget(self.card_used, 1, 1)

        layout.addWidget(QLabel("締日"), 0, 2)
        layout.addWidget(self.card_closing, 1, 2)

        layout.addWidget(QLabel("支払日"), 0, 3)
        layout.addWidget(self.card_payment, 1, 3)

        layout.addWidget(add_btn, 1, 4)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)

        return box

    def investment_form(self):
        box = QGroupBox("投資資産を追加")
        box.setObjectName("formCard")

        layout = QGridLayout(box)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(10)

        self.inv_name = QLineEdit()
        self.inv_name.setPlaceholderText("例: eMAXIS Slim S&P500")

        self.inv_kind = QComboBox()
        self.inv_kind.addItems(["NISA", "iDeCo", "株式", "投資信託", "ETF", "暗号資産", "その他"])

        self.inv_quantity = QDoubleSpinBox()
        self.inv_quantity.setMaximum(999999999)
        self.inv_quantity.setDecimals(4)

        self.inv_cost = QDoubleSpinBox()
        self.inv_cost.setMaximum(999999999)
        self.inv_cost.setSuffix(" 円")

        self.inv_current = QDoubleSpinBox()
        self.inv_current.setMaximum(999999999)
        self.inv_current.setSuffix(" 円")

        add_btn = QPushButton("追加")
        add_btn.setObjectName("primaryLarge")
        add_btn.clicked.connect(self.add_investment)

        layout.addWidget(QLabel("銘柄名"), 0, 0)
        layout.addWidget(self.inv_name, 1, 0)

        layout.addWidget(QLabel("種類"), 0, 1)
        layout.addWidget(self.inv_kind, 1, 1)

        layout.addWidget(QLabel("数量"), 0, 2)
        layout.addWidget(self.inv_quantity, 1, 2)

        layout.addWidget(QLabel("取得金額"), 2, 0)
        layout.addWidget(self.inv_cost, 3, 0)

        layout.addWidget(QLabel("評価額"), 2, 1)
        layout.addWidget(self.inv_current, 3, 1)

        layout.addWidget(add_btn, 3, 2)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)

        return box

 
    def add_account(self):
        name = self.acc_name.text().strip()
        if not name:
            QMessageBox.warning(self, "入力エラー", "名前を入力してください。")
            return

        self.db.execute("""
            INSERT INTO accounts(name, kind, balance, note, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name, self.acc_kind.currentText(), self.acc_balance.value(),
            "", datetime.now().isoformat()
        ))
        self.acc_name.clear()
        self.acc_balance.setValue(0)
        self.refresh_callback()

    def add_card(self):
        name = self.card_name.text().strip()
        if not name:
            QMessageBox.warning(self, "入力エラー", "カード名を入力してください。")
            return

        self.db.execute("""
            INSERT INTO credit_cards(name, used_amount, closing_day, payment_day, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name, self.card_used.value(), self.card_closing.value(),
            self.card_payment.value(), "", datetime.now().isoformat()
        ))
        self.card_name.clear()
        self.card_used.setValue(0)
        self.refresh_callback()

    def add_investment(self):
        name = self.inv_name.text().strip()
        if not name:
            QMessageBox.warning(self, "入力エラー", "銘柄名を入力してください。")
            return

        self.db.execute("""
            INSERT INTO investments(name, kind, quantity, cost, current_value, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, self.inv_kind.currentText(), self.inv_quantity.value(),
            self.inv_cost.value(), self.inv_current.value(), "",
            datetime.now().isoformat()
        ))
        self.inv_name.clear()
        self.inv_quantity.setValue(0)
        self.inv_cost.setValue(0)
        self.inv_current.setValue(0)
        self.refresh_callback()

    def refresh(self):
        rows = []

        for r in self.db.fetchall("SELECT * FROM accounts ORDER BY id DESC"):
            rows.append(("account", r["id"], r["name"], r["kind"], r["balance"], "", ""))

        for r in self.db.fetchall("SELECT * FROM credit_cards ORDER BY id DESC"):
            rows.append(("card", r["id"], r["name"], "クレジットカード", -r["used_amount"], f"締日 {r['closing_day']}日", f"支払日 {r['payment_day']}日"))

        for r in self.db.fetchall("SELECT * FROM investments ORDER BY id DESC"):
            profit = r["current_value"] - r["cost"]

            if r["cost"] > 0:
                profit_rate = profit / r["cost"] * 100
            else:
                profit_rate = 0

            profit_text = f"損益 {money(profit)} / {profit_rate:.1f}%"

            rows.append((
                "investment",
                r["id"],
                r["name"],
                r["kind"],
                r["current_value"],
                profit_text,
                f"数量 {r['quantity']}"
            ))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["種別ID", "ID", "名前", "種類", "評価額/残高", "補足1", "補足2"])
        self.table.setRowCount(len(rows))

        for y, row in enumerate(rows):
            for x, val in enumerate(row):
                if x == 4:
                    text = money(val)
                else:
                    text = str(val)

                item = QTableWidgetItem(text)

                if x == 0:
                    item.setData(Qt.UserRole, val)
                    if val == "account":
                        item.setText("口座")
                    elif val == "card":
                        item.setText("クレカ")
                    elif val == "investment":
                        item.setText("投資")

                if x == 4:
                    if float(val) < 0:
                        item.setForeground(QColor("#EB5757"))
                    else:
                        item.setForeground(QColor("#27AE60"))

                self.table.setItem(y, x, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(1, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)

        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 48)

    def selected_asset(self):
        row = self.table.currentRow()
        if row < 0:
            return None, None

        kind_item = self.table.item(row, 0)
        id_item = self.table.item(row, 1)

        if not kind_item or not id_item:
            return None, None

        kind = kind_item.data(Qt.UserRole)

        if not kind:
            text = kind_item.text()
            if text == "口座":
                kind = "account"
            elif text == "クレカ":
                kind = "card"
            elif text == "投資":
                kind = "investment"
            else:
                kind = text

        item_id = int(id_item.text())

        return kind, item_id
    
    def edit_selected(self):
        kind, item_id = self.selected_asset()

        if not kind or not item_id:
            QMessageBox.information(self, "未選択", "編集する資産を選択してください。")
            return

        dlg = AssetEditDialog(self.db, kind, item_id)

        if dlg.exec() == QDialog.Accepted:
            self.refresh_callback()

    def delete_selected(self):
        kind, item_id = self.selected_asset()

        if not kind or not item_id:
            QMessageBox.information(self, "未選択", "削除する資産を選択してください。")
            return

        if QMessageBox.question(self, "確認", "選択した資産を削除しますか？") != QMessageBox.Yes:
            return

        if kind == "account":
            self.db.execute("DELETE FROM accounts WHERE id = ?", (item_id,))
        elif kind == "card":
            self.db.execute("DELETE FROM credit_cards WHERE id = ?", (item_id,))
        elif kind == "investment":
            self.db.execute("DELETE FROM investments WHERE id = ?", (item_id,))

        self.refresh_callback()


class TransactionDialog(QDialog):
    def __init__(self, db, tx=None):
        super().__init__()
        self.db = db
        self.tx = tx
        self.setWindowTitle("取引入力")
        self.resize(480, 520)

        layout = QVBoxLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.type_combo = QComboBox()
        self.type_combo.addItems(["expense", "income", "transfer"])
        self.type_combo.currentTextChanged.connect(self.update_category_options)

        self.amount = QDoubleSpinBox()
        self.amount.setMaximum(999999999)
        self.amount.setSuffix(" 円")

        self.category = QComboBox()
        self.memo = QTextEdit()
        self.memo.setPlaceholderText("メモ")

        self.from_combo = QComboBox()
        self.to_combo = QComboBox()

        layout.addWidget(QLabel("日付"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("種類"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("金額"))
        layout.addWidget(self.amount)
        layout.addWidget(QLabel("カテゴリ"))
        layout.addWidget(self.category)
        layout.addWidget(QLabel("支払元 / 振替元"))
        layout.addWidget(self.from_combo)
        layout.addWidget(QLabel("入金先 / 振替先"))
        layout.addWidget(self.to_combo)
        layout.addWidget(QLabel("メモ"))
        layout.addWidget(self.memo)

        btn = QPushButton("保存")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.load_accounts()
        self.update_category_options()

        if tx:
            self.load_tx(tx)

    def load_accounts(self):
        self.from_combo.clear()
        self.to_combo.clear()

        self.from_combo.addItem("なし", None)
        self.to_combo.addItem("なし", None)

        for r in self.db.fetchall("SELECT * FROM accounts ORDER BY name"):
            value = ("account", r["id"])
            label = f"{r['name']} ({r['kind']})"
            self.from_combo.addItem(label, value)
            self.to_combo.addItem(label, value)

        for r in self.db.fetchall("SELECT * FROM credit_cards ORDER BY name"):
            value = ("card", r["id"])
            label = f"{r['name']} (クレカ)"
            self.from_combo.addItem(label, value)

    def update_category_options(self):
        typ = self.type_combo.currentText()
        self.category.clear()
        rows = self.db.fetchall(
            "SELECT name FROM categories WHERE type = ? ORDER BY name",
            (typ,)
        )
        for r in rows:
            self.category.addItem(r["name"])

    def load_tx(self, tx):
        y, m, d = map(int, tx["date"].split("-"))
        self.date_edit.setDate(QDate(y, m, d))
        self.type_combo.setCurrentText(tx["type"])
        self.amount.setValue(float(tx["amount"]))
        self.update_category_options()

        idx = self.category.findText(tx["category"] or "")
        if idx >= 0:
            self.category.setCurrentIndex(idx)

        self.memo.setPlainText(tx["memo"] or "")

        self.select_combo(self.from_combo, tx["from_kind"], tx["from_id"])
        self.select_combo(self.to_combo, tx["to_kind"], tx["to_id"])

    def select_combo(self, combo, kind, ident):
        for i in range(combo.count()):
            value = combo.itemData(i)
            if value and value[0] == kind and value[1] == ident:
                combo.setCurrentIndex(i)
                return

    def get_data(self):
        from_data = self.from_combo.currentData()
        to_data = self.to_combo.currentData()

        return {
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "type": self.type_combo.currentText(),
            "amount": self.amount.value(),
            "category": self.category.currentText(),
            "memo": self.memo.toPlainText().strip(),
            "from_kind": from_data[0] if from_data else None,
            "from_id": from_data[1] if from_data else None,
            "to_kind": to_data[0] if to_data else None,
            "to_id": to_data[1] if to_data else None,
            "created_at": datetime.now().isoformat()
        }


class TransactionTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback

        layout = QVBoxLayout(self)
        title = QLabel("収支管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        top = QHBoxLayout()
        add_btn = QPushButton("取引を追加")
        add_btn.clicked.connect(self.add_transaction)
        edit_btn = QPushButton("選択を編集")
        edit_btn.clicked.connect(self.edit_transaction)
        delete_btn = QPushButton("選択を削除")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self.delete_transaction)

        self.search = QLineEdit()
        self.search.setPlaceholderText("検索: メモ / カテゴリ")
        self.search.textChanged.connect(self.refresh)

        top.addWidget(add_btn)
        top.addWidget(edit_btn)
        top.addWidget(delete_btn)
        top.addWidget(self.search)
        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        keyword = self.search.text().strip()
        if keyword:
            rows = self.db.fetchall("""
                SELECT * FROM transactions
                WHERE memo LIKE ? OR category LIKE ?
                ORDER BY date DESC, id DESC
            """, (f"%{keyword}%", f"%{keyword}%"))
        else:
            rows = self.db.fetchall("""
                SELECT * FROM transactions
                ORDER BY date DESC, id DESC
            """)

        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "日付", "種類", "金額", "カテゴリ", "メモ", "経路"])
        self.table.setRowCount(len(rows))

        for y, r in enumerate(rows):
            route = self.route_text(r)
            vals = [
                r["id"], r["date"], self.type_label(r["type"]),
                money(r["amount"]), r["category"] or "", r["memo"] or "", route
            ]
            for x, v in enumerate(vals):
                self.table.setItem(y, x, QTableWidgetItem(str(v)))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def type_label(self, typ):
        return {
            "expense": "支出",
            "income": "入金",
            "transfer": "振替"
        }.get(typ, typ)

    def route_text(self, r):
        if r["type"] == "expense":
            return self.name_of(r["from_kind"], r["from_id"]) + " から支払い"
        if r["type"] == "income":
            return self.name_of(r["to_kind"], r["to_id"]) + " へ入金"
        if r["type"] == "transfer":
            return self.name_of(r["from_kind"], r["from_id"]) + " → " + self.name_of(r["to_kind"], r["to_id"])
        return ""

    def name_of(self, kind, ident):
        if not kind or not ident:
            return "なし"
        if kind == "account":
            r = self.db.fetchone("SELECT name FROM accounts WHERE id = ?", (ident,))
            return r["name"] if r else "不明"
        if kind == "card":
            r = self.db.fetchone("SELECT name FROM credit_cards WHERE id = ?", (ident,))
            return r["name"] if r else "不明"
        return "不明"

    def add_transaction(self):
        dlg = TransactionDialog(self.db)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if data["amount"] <= 0:
                QMessageBox.warning(self, "入力エラー", "金額を入力してください。")
                return

            cur = self.db.execute("""
                INSERT INTO transactions
                (date, type, amount, category, memo, from_kind, from_id, to_kind, to_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["date"], data["type"], data["amount"], data["category"], data["memo"],
                data["from_kind"], data["from_id"], data["to_kind"], data["to_id"],
                data["created_at"]
            ))
            data["id"] = cur.lastrowid
            self.db.apply_transaction_effect(data, sign=1)
            self.refresh_callback()

    def selected_tx_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def edit_transaction(self):
        tx_id = self.selected_tx_id()
        if not tx_id:
            return

        old = self.db.fetchone("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        dlg = TransactionDialog(self.db, old)

        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if data["amount"] <= 0:
                QMessageBox.warning(self, "入力エラー", "金額を入力してください。")
                return

            old_dict = dict(old)
            self.db.apply_transaction_effect(old_dict, sign=-1)

            self.db.execute("""
                UPDATE transactions
                SET date = ?, type = ?, amount = ?, category = ?, memo = ?,
                    from_kind = ?, from_id = ?, to_kind = ?, to_id = ?
                WHERE id = ?
            """, (
                data["date"], data["type"], data["amount"], data["category"], data["memo"],
                data["from_kind"], data["from_id"], data["to_kind"], data["to_id"],
                tx_id
            ))

            data["id"] = tx_id
            self.db.apply_transaction_effect(data, sign=1)
            self.refresh_callback()

    def delete_transaction(self):
        tx_id = self.selected_tx_id()
        if not tx_id:
            return

        if QMessageBox.question(self, "確認", "選択した取引を削除しますか？") != QMessageBox.Yes:
            return

        tx = self.db.fetchone("SELECT * FROM transactions WHERE id = ?", (tx_id,))
        if tx:
            self.db.apply_transaction_effect(dict(tx), sign=-1)
            self.db.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        self.refresh_callback()


class AnalysisTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout(self)
        title = QLabel("分析")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.figure = Figure(figsize=(10, 8), facecolor="#151A20")
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        refresh_btn = QPushButton("グラフ更新")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)

    def refresh(self):
        self.figure.clear()
        self.draw_expense_pie()
        self.draw_asset_pie()
        self.draw_monthly_balance()
        self.canvas.draw()

    def draw_expense_pie(self):
        ax = self.figure.add_subplot(221)
        ax.set_facecolor("#151A20")

        month = date.today().strftime("%Y-%m")
        rows = self.db.fetchall("""
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE type = 'expense' AND substr(date, 1, 7) = ?
            GROUP BY category
        """, (month,))

        if rows:
            labels = [r["category"] or "未分類" for r in rows]
            values = [r["total"] for r in rows]
            ax.pie(values, labels=labels, autopct="%1.1f%%", textprops={"color": "white"})
        else:
            ax.text(0.5, 0.5, "支出データなし", ha="center", va="center", color="white")
        ax.set_title("今月の支出割合", color="white")

    def draw_asset_pie(self):
        ax = self.figure.add_subplot(222)
        ax.set_facecolor("#151A20")

        cash = self.db.fetchone("SELECT COALESCE(SUM(balance), 0) AS total FROM accounts")["total"]
        inv = self.db.fetchone("SELECT COALESCE(SUM(current_value), 0) AS total FROM investments")["total"]
        card = self.db.fetchone("SELECT COALESCE(SUM(used_amount), 0) AS total FROM credit_cards")["total"]

        labels = []
        values = []

        if cash > 0:
            labels.append("口座/PayPay")
            values.append(cash)
        if inv > 0:
            labels.append("投資")
            values.append(inv)
        if card > 0:
            labels.append("クレカ利用額")
            values.append(card)

        if values:
            ax.pie(values, labels=labels, autopct="%1.1f%%", textprops={"color": "white"})
        else:
            ax.text(0.5, 0.5, "資産データなし", ha="center", va="center", color="white")
        ax.set_title("資産構成", color="white")

    def draw_monthly_balance(self):
        ax = self.figure.add_subplot(212)
        ax.set_facecolor("#151A20")

        rows = self.db.fetchall("""
            SELECT substr(date, 1, 7) AS ym,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS income,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS expense
            FROM transactions
            GROUP BY ym
            ORDER BY ym
        """)

        if rows:
            months = [r["ym"] for r in rows]
            balances = [r["income"] - r["expense"] for r in rows]
            ax.plot(months, balances, marker="o")
            ax.axhline(0)
            ax.tick_params(axis="x", rotation=30, colors="white")
        else:
            ax.text(0.5, 0.5, "収支データなし", ha="center", va="center", color="white")

        ax.set_title("月別収支差額", color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#303C47")


class SettingsTab(QWidget):
    def __init__(self, db, refresh_callback):
        super().__init__()
        self.db = db
        self.refresh_callback = refresh_callback

        layout = QVBoxLayout(self)
        title = QLabel("設定")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        box = QGroupBox("カテゴリ追加")
        form = QVBoxLayout(box)

        self.category_name = QLineEdit()
        self.category_name.setPlaceholderText("例: カフェ")
        self.category_type = QComboBox()
        self.category_type.addItems(["expense", "income", "transfer"])

        add_btn = QPushButton("カテゴリ追加")
        add_btn.clicked.connect(self.add_category)

        form.addWidget(QLabel("カテゴリ名"))
        form.addWidget(self.category_name)
        form.addWidget(QLabel("種類"))
        form.addWidget(self.category_type)
        form.addWidget(add_btn)

        layout.addWidget(box)

        budget_box = QGroupBox("月間予算")
        bform = QVBoxLayout(budget_box)

        self.budget_category = QComboBox()
        self.budget_amount = QDoubleSpinBox()
        self.budget_amount.setMaximum(999999999)
        self.budget_amount.setSuffix(" 円")

        budget_btn = QPushButton("予算保存")
        budget_btn.clicked.connect(self.save_budget)

        bform.addWidget(QLabel("カテゴリ"))
        bform.addWidget(self.budget_category)
        bform.addWidget(QLabel("月予算"))
        bform.addWidget(self.budget_amount)
        bform.addWidget(budget_btn)

        layout.addWidget(budget_box)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        help_box = QGroupBox("ヘルプ")
        help_layout = QVBoxLayout(help_box)

        help_label = QLabel("MoneyFlowの使い方、登録方法、バックアップ方法を確認できます。")
        help_label.setStyleSheet("color: #AEB8C2;")

        help_btn = QPushButton("使い方を表示")
        help_btn.clicked.connect(self.open_help)

        help_layout.addWidget(help_label)
        help_layout.addWidget(help_btn)

        layout.addWidget(help_box)

    def open_help(self):
        dlg = HelpDialog()
        dlg.exec()

    def refresh(self):
        self.budget_category.clear()
        cats = self.db.fetchall("SELECT name FROM categories WHERE type = 'expense' ORDER BY name")
        for c in cats:
            self.budget_category.addItem(c["name"])

        rows = self.db.fetchall("""
            SELECT c.name, c.type, COALESCE(b.monthly_limit, 0) AS monthly_limit
            FROM categories c
            LEFT JOIN budgets b ON b.category = c.name
            ORDER BY c.type, c.name
        """)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["カテゴリ", "種類", "月予算"])
        self.table.setRowCount(len(rows))

        for y, r in enumerate(rows):
            self.table.setItem(y, 0, QTableWidgetItem(r["name"]))
            self.table.setItem(y, 1, QTableWidgetItem(r["type"]))
            self.table.setItem(y, 2, QTableWidgetItem(money(r["monthly_limit"])))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_category(self):
        name = self.category_name.text().strip()
        if not name:
            return

        try:
            self.db.execute(
                "INSERT INTO categories(name, type) VALUES (?, ?)",
                (name, self.category_type.currentText())
            )
            self.category_name.clear()
            self.refresh_callback()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "エラー", "同じカテゴリがすでに存在します。")

    def save_budget(self):
        category = self.budget_category.currentText()
        amount = self.budget_amount.value()

        self.db.execute("""
            INSERT INTO budgets(category, monthly_limit)
            VALUES (?, ?)
            ON CONFLICT(category)
            DO UPDATE SET monthly_limit = excluded.monthly_limit
        """, (category, amount))

        self.refresh_callback()


def main():
    setup_japanese_font()
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MoneyFlowApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()