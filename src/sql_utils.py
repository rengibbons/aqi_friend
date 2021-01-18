"""
Author: Ren Gibbons
Email: gibbons.ren@gmail.com
Date Created: 2021-01-17

Helpful reference links:
    https://www.sqlitetutorial.net/sqlite-python/
"""
import sqlite3
import pandas as pd

CONN = sqlite3.connect('../data/air_dev_quality.db')
TABLE_COLS = ("time", "temperature", "pressure", "humidity", "pm25", "pm10", "aqi")


def create_table(table:str="air_quality"):
    """
    Creates a SQLite table.

    Args:
        table: name of the SQLite table

    Returns:
        None
    """
    sql = f""" CREATE TABLE IF NOT EXISTS {table} (
                 id integer PRIMARY KEY,
                 time text,
                 temperature real,
                 pressure real,
                 humidity real,
                 pm25 real,
                 pm10 real,
                 aqi integer
              ); """

    cursor = CONN.cursor()
    cursor.execute(sql)


def insert_air_quality_reading(air_quality: tuple):
    """
    Creates a SQLite air quality reading observation.
    
    Args:
        air_quality: tuple with all air quality data to be logged
    
    Returns:
        None
    """
    create_table() # creates table if it doesn't exist
    columns_str = ", ".join(col for col in TABLE_COLS)
    sql = f"INSERT INTO air_quality({columns_str}) VALUES(?,?,?,?,?,?,?)"
    cursor = CONN.cursor()
    cursor.execute(sql, air_quality)
    CONN.commit()


def select_all_table_data(table:str="air_quality"):
    """
    Querys all rows in the air_quality table.
    
    Args:
        table: name of the SQLite table
    
    Returns:
        pd.DataFrame with all data
    """
    cursor = CONN.cursor()
    cursor.execute(f"SELECT * FROM {table}")

    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=("id",)+TABLE_COLS)
    df.set_index("id", inplace=True)
    return df


def delete_air_quality_reading(id:int):
    """
    Deletes a reading by task id.
    
    Args:
        id: int to the row id to delete
        
    Returns:
        None
    """
    sql = "DELETE FROM tasks WHERE id=?"
    cursor = CONN.cursor()
    cursor.execute(sql, (id,))
    CONN.commit()


def close_db_connection():
    """ Closes the connection to the database. """
    CONN.close()


def main():
    """
    Tests out the primary functions of the SQLite script. main() not
    called in during scheduled runs.
    """
    create_table()
    data = ("2021-01-16 20:56:05", 71.1, 32.4, 55.4, 11.2, 9.3, 33)
    insert_air_quality_reading(data)
    df = select_all_table_data()
    print(df)
    close_db_connection()

if __name__ == "__main__":
    main()

