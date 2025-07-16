"""
Database connection and configuration for Cyberia FastAPI
"""

import pyodbc
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    'server': 'SA',
    'database': 'Cyberia',
    'username': 'SA',
    'password': 'Mar120305!',
    'driver': '{ODBC Driver 17 for SQL Server}',
    'trust_server_certificate': 'yes'
}

def get_connection_string() -> str:
    """Build SQL Server connection string"""
    return (
        f"DRIVER={DATABASE_CONFIG['driver']};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={DATABASE_CONFIG['database']};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']};"
        f"TrustServerCertificate={DATABASE_CONFIG['trust_server_certificate']}"
    )

def get_db_connection():
    """Get database connection"""
    try:
        conn_str = get_connection_string()
        connection = pyodbc.connect(conn_str)
        logger.info("Database connection established successfully")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

class DatabaseManager:
    """Database manager for handling connections and queries"""
    
    def __init__(self):
        self.connection_string = get_connection_string()
    
    async def execute_query(self, query: str, params: Optional[tuple] = None, fetch: str = "all"):
        """Execute SQL query and return results"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch == "one":
                    result = cursor.fetchone()
                    return dict(zip([column[0] for column in cursor.description], result)) if result else None
                elif fetch == "all":
                    results = cursor.fetchall()
                    columns = [column[0] for column in cursor.description]
                    return [dict(zip(columns, row)) for row in results]
                elif fetch == "none":
                    conn.commit()
                    return cursor.rowcount
                else:
                    raise ValueError(f"Invalid fetch type: {fetch}")
                    
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    async def execute_procedure(self, procedure_name: str, params: Optional[tuple] = None):
        """Execute stored procedure"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(f"EXEC {procedure_name} {','.join(['?' for _ in params])}", params)
                else:
                    cursor.execute(f"EXEC {procedure_name}")
                
                # Get all result sets
                results = []
                while True:
                    try:
                        rows = cursor.fetchall()
                        if rows:
                            columns = [column[0] for column in cursor.description]
                            results.append([dict(zip(columns, row)) for row in rows])
                        if not cursor.nextset():
                            break
                    except pyodbc.ProgrammingError:
                        break
                
                conn.commit()
                return results if len(results) > 1 else (results[0] if results else [])
                
        except Exception as e:
            logger.error(f"Stored procedure execution failed: {e}")
            logger.error(f"Procedure: {procedure_name}")
            logger.error(f"Params: {params}")
            raise

# Global database manager instance
db_manager = DatabaseManager()