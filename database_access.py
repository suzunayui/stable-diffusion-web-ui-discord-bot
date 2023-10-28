# database_access.py

import sqlite3

class UserSettingsDatabase:
    def __init__(self, db_file):
        self.db_file = db_file  # db_fileパラメータをself.db_fileに代入
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER,
                guild_id INTEGER,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                PRIMARY KEY (user_id, guild_id, setting_key)
            )
        ''')
        self.conn.commit()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

    def add_setting(self, user_id, guild_id, key, value):
        # まずレコードが存在するかを確認
        existing_value = self.get_setting(user_id, guild_id, key)

        if existing_value is not None:
            # 既に存在する場合はUPDATEを実行
            self.update_setting(user_id, guild_id, key, value)
        else:
            # 存在しない場合はINSERTを実行
            self.cursor.execute("INSERT INTO user_settings (user_id, guild_id, setting_key, setting_value) VALUES (?, ?, ?, ?)", (user_id, guild_id, key, value))
            self.conn.commit()

    def get_setting(self, user_id, guild_id, key):
        self.cursor.execute("SELECT setting_value FROM user_settings WHERE user_id = ? AND guild_id = ? AND setting_key = ?", (user_id, guild_id, key))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    # 削除予定
    def update_setting(self, user_id, guild_id, key, value):
        self.cursor.execute("UPDATE user_settings SET setting_value = ? WHERE user_id = ? AND guild_id = ? AND setting_key = ?", (value, user_id, guild_id, key))
        self.conn.commit()

    # 削除予定
    def delete_setting(self, user_id, guild_id, key):
        self.cursor.execute("DELETE FROM user_settings WHERE user_id = ? AND guild_id = ? AND setting_key = ?", (user_id, guild_id, key))
        self.conn.commit()

    # 削除予定
    def close(self):
        self.conn.close()