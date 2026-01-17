import aiosqlite
from asyncio import Lock

database = "bot_data.db"


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.lock = Lock()  # Lock for protecting simultaneous operations on the database

    async def connect(self):
        """Open the database connection and configure the environment."""
        self.conn = await aiosqlite.connect(self.db_name, timeout=10)  # Extend timeout for long-running tasks
        await self.conn.execute("PRAGMA journal_mode=WAL;")  # Enable WAL (Write-Ahead Logging) mode
        await self.conn.execute("PRAGMA foreign_keys = ON;")  # Ensure foreign key integrity

        # Dynamically migrate the database schema to create necessary tables and handle updates
        await self.__migrate_schema()

    async def __migrate_schema(self):
        """Handles creating/updating the database schema based on current requirements."""
        # Create tables dynamically if not already present
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER,
                role_name TEXT,
                PRIMARY KEY (user_id, role_name)
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_balances (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reason TEXT
            )
        """)
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS casamentos (
                user1_id INTEGER,
                user2_id INTEGER,
                PRIMARY KEY (user1_id, user2_id)
            )
        """)
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS halloween_data (
        user_id INTEGER,
        points_number INTEGER,
        PRIMARY KEY (user_id)
        )""")
        await self.conn.execute("""
        CREATE TABLE IF NOT EXISTS halloween_cooldowns (
        user_id INTEGER PRIMARY KEY,
        last_used INTEGER
        )""")

        # Add missing columns dynamically if required (e.g., hint_cooldown)
        try:
            # Attempt adding the 'hint_cooldown' column dynamically
            await self.conn.execute("ALTER TABLE user_data ADD COLUMN hint_cooldown INTEGER DEFAULT 0;")
        except aiosqlite.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✅ Column 'hint_cooldown' already exists in 'user_data'.")
            else:
                print(f"❌ Error during schema migration: {e}")

        await self.conn.commit()

    async def close(self):
        """Close the database connection."""
        if self.conn:
            await self.conn.close()

    async def execute(self, query, params=None):
        """Execute a query without a return (INSERT, UPDATE, DELETE). Protected by Lock."""
        params = params or ()
        async with self.lock:  # Ensure only one concurrent execution
            try:
                await self.conn.execute(query, params)
                await self.conn.commit()
            except Exception as e:
                print(f"Error executing query: {query} - {e}")

    async def fetchone(self, query, params=None):
        """Execute a query and return a single result."""
        params = params or ()
        async with self.lock:
            try:
                async with self.conn.execute(query, params) as cursor:
                    return await cursor.fetchone()
            except Exception as e:
                print(f"Error fetching a single item: {query} - {e}")
                return None

    async def fetchall(self, query, params=None):
        """Execute a query and return multiple results."""
        params = params or ()
        async with self.lock:
            try:
                async with self.conn.execute(query, params) as cursor:
                    return await cursor.fetchall()
            except Exception as e:
                print(f"Error fetching multiple items: {query} - {e}")
                return []


# Initializing the database
db = Database('bot_data.db')


async def initialize_db():
    """Function to initialize the database."""
    await db.connect()