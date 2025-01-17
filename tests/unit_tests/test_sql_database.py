# flake8: noqa=E501
"""Test SQL database wrapper."""

from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, insert

from langchain.sql_database import _TEMPLATE_PREFIX, SQLDatabase

metadata_obj = MetaData()

user = Table(
    "user",
    metadata_obj,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", String(16), nullable=False),
)

company = Table(
    "company",
    metadata_obj,
    Column("company_id", Integer, primary_key=True),
    Column("company_location", String, nullable=False),
)


def test_table_info() -> None:
    """Test that table info is constructed properly."""
    engine = create_engine("sqlite:///:memory:")
    metadata_obj.create_all(engine)
    db = SQLDatabase(engine)
    output = db.table_info
    expected_output = """
    CREATE TABLE user (                                                                                                                                    
            user_id INTEGER NOT NULL,
            user_name VARCHAR(16) NOT NULL,
            PRIMARY KEY (user_id)
    )

    SELECT * FROM 'user' LIMIT 3
    user_id user_name


    CREATE TABLE company (
            company_id INTEGER NOT NULL,
            company_location VARCHAR NOT NULL,
            PRIMARY KEY (company_id)
    )

    SELECT * FROM 'company' LIMIT 3
    company_id company_location
    """

    assert sorted(" ".join(output.split())) == sorted(" ".join(expected_output.split()))


def test_table_info_w_sample_rows() -> None:
    """Test that table info is constructed properly."""
    engine = create_engine("sqlite:///:memory:")
    metadata_obj.create_all(engine)
    values = [
        {"user_id": 13, "user_name": "Harrison"},
        {"user_id": 14, "user_name": "Chase"},
    ]
    stmt = insert(user).values(values)
    with engine.begin() as conn:
        conn.execute(stmt)

    db = SQLDatabase(engine, sample_rows_in_table_info=2)

    output = db.table_info

    expected_output = """
        CREATE TABLE company (
        company_id INTEGER NOT NULL,
        company_location VARCHAR NOT NULL,
        PRIMARY KEY (company_id)
)

        SELECT * FROM 'company' LIMIT 2
        company_id company_location


        CREATE TABLE user (
        user_id INTEGER NOT NULL,
        user_name VARCHAR(16) NOT NULL,
        PRIMARY KEY (user_id)
        )

        SELECT * FROM 'user' LIMIT 2
        user_id user_name
        13 Harrison
        14 Chase
        """

    assert sorted(output.split()) == sorted(expected_output.split())


def test_sql_database_run() -> None:
    """Test that commands can be run successfully and returned in correct format."""
    engine = create_engine("sqlite:///:memory:")
    metadata_obj.create_all(engine)
    stmt = insert(user).values(user_id=13, user_name="Harrison")
    with engine.begin() as conn:
        conn.execute(stmt)
    db = SQLDatabase(engine)
    command = "select user_name from user where user_id = 13"
    output = db.run(command)
    expected_output = "[('Harrison',)]"
    assert output == expected_output


def test_sql_database_run_update() -> None:
    """Test commands which return no rows return an empty string."""
    engine = create_engine("sqlite:///:memory:")
    metadata_obj.create_all(engine)
    stmt = insert(user).values(user_id=13, user_name="Harrison")
    with engine.begin() as conn:
        conn.execute(stmt)
    db = SQLDatabase(engine)
    command = "update user set user_name='Updated' where user_id = 13"
    output = db.run(command)
    expected_output = ""
    assert output == expected_output
