import sqlite3
import pandas as pd


DATABASE_PATH = "data/source_system/erp.db"


def inspect_database():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    tables = pd.read_sql(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """,
        connection
    )

    print("\nERP DATABASE TABLES")
    print("=" * 50)

    for table in tables["name"]:

        print(f"\nTable: {table}")

        df = pd.read_sql(
            f"SELECT * FROM {table} LIMIT 5",
            connection
        )

        print(df)

    connection.close()


if __name__ == "__main__":
    inspect_database()