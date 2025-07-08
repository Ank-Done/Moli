"""
Program: Database Connection Manager
Objective: Handle database connections for sugar company BI system
Author: Francisco Gonzalez Gonzalez
Date: 2025-01-07
Module: Database connectivity and configuration management
"""

"""
Modification Date: 2025-01-07
Author: Francisco Gonzalez Gonzalez
Purpose: Initial creation following coding standard
Change: Created centralized database connection management
"""

import mysql.connector

"""
Database Configuration Section
This section handles the configuration parameters for connecting
to the reporteventasenejul database used by the sugar company
"""

# Database configuration for sugar company system
databaseConfiguration = {
    'host': 'localhost',           # Database server host address
    'user': 'root',               # Database user account
    'password': 'Mar120305',      # Database password for authentication
    'database': 'reporteventasenejul',  # Sugar company database name
    'port': 3306                  # MySQL default port number
}

def getDatabaseConnection():
    """
    Purpose: Establish and return database connection to sugar company database
    Limitations: Requires MySQL server running on localhost port 3306
    Returns: MySQL connection object if successful, None if failed
    Dependencies: mysql.connector library, valid database credentials
    Re-entrant: Yes, can be called multiple times safely
    """
    try:
        # Attempt to establish connection using configuration parameters
        databaseConnection = mysql.connector.connect(**databaseConfiguration)
        return databaseConnection
    except Exception as connectionError:
        # Log connection error for debugging purposes
        print(f"Database connection error: {connectionError}")
        return None

def testDatabaseConnection():
    """
    Purpose: Test database connectivity and verify system status
    Limitations: None, safe to call for testing purposes
    Returns: True if connection successful, False otherwise
    Dependencies: getDatabaseConnection function, active database
    Re-entrant: Yes, safe for multiple calls
    """
    testConnection = getDatabaseConnection()  # Get connection for testing
    
    if testConnection:
        try:
            # Create cursor for executing test query
            testCursor = testConnection.cursor()
            
            # Execute simple test query to verify connectivity
            testCursor.execute("SELECT 1")
            testResult = testCursor.fetchone()  # Retrieve test result
            
            # Cleanup resources after test
            testCursor.close()
            testConnection.close()
            
            return True
        except Exception as testError:
            print(f"Database test error: {testError}")
            return False
    else:
        return False

def getTablesList():
    """
    Purpose: Retrieve list of available tables in sugar company database
    Limitations: Requires valid database connection and proper permissions
    Returns: List of table names if successful, empty list if failed
    Dependencies: getDatabaseConnection function, database access rights
    Re-entrant: Yes, safe for concurrent access
    """
    tablesList = []  # Initialize empty list for table names
    databaseConnection = getDatabaseConnection()  # Establish connection
    
    if databaseConnection:
        try:
            # Create cursor for table listing query
            tablesCursor = databaseConnection.cursor()
            
            # Execute query to show all tables in database
            tablesCursor.execute("SHOW TABLES")
            tablesResults = tablesCursor.fetchall()  # Get all table names
            
            # Extract table names from query results
            for tableRow in tablesResults:
                tablesList.append(list(tableRow.values())[0])
            
            # Cleanup database resources
            tablesCursor.close()
            databaseConnection.close()
            
        except Exception as tablesError:
            print(f"Error retrieving tables list: {tablesError}")
    
    return tablesList