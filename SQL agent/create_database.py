from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String

# Define the database file name
DATABASE_FILE = "my_sample_database.db"

# Create an SQLite database engine
# The '///' indicates a relative path to the database file (in your current directory)
engine = create_engine(f"sqlite:///{DATABASE_FILE}")

# Use MetaData to manage tables programmatically
metadata = MetaData()

# Define the 'employees' table schema
employees_table = Table(
    'employees', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('department', String),
    Column('salary', Integer)
)

# Define the 'departments' table schema
departments_table = Table(
    'departments', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String)
)

# Create all defined tables in the database
print(f"Creating database tables in {DATABASE_FILE}...")
metadata.create_all(engine)
print("Tables created successfully.")

# Insert sample data into the 'departments' table
print("Inserting data into 'departments' table...")
with engine.connect() as connection:
    connection.execute(text("""
        INSERT INTO departments (id, name) VALUES
        (1, 'Sales'),
        (2, 'Marketing'),
        (3, 'Engineering'),
        (4, 'HR');
    """))
    connection.commit() # Save changes to the database
print("Departments data inserted.")

# Insert sample data into the 'employees' table
print("Inserting data into 'employees' table...")
with engine.connect() as connection:
    connection.execute(text("""
        INSERT INTO employees (id, name, department, salary) VALUES
        (1, 'Alice', 'Sales', 60000),
        (2, 'Bob', 'Marketing', 55000),
        (3, 'Charlie', 'Engineering', 75000),
        (4, 'David', 'Sales', 62000),
        (5, 'Eve', 'HR', 50000),
        (6, 'Frank', 'Engineering', 80000),
        (7, 'Grace', 'Marketing', 58000);
    """))
    connection.commit() # Save changes to the database
print("Employees data inserted.")

print(f"Database '{DATABASE_FILE}' created and populated with sample data.")