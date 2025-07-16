"""
User service for managing users and customers
"""

import logging
from typing import List, Optional
from config.database import db_manager
from schemas.users import UserResponse, CustomerResponse

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users and customers"""
    
    async def get_users(self, user_type: Optional[str] = None, is_active: bool = True) -> List[UserResponse]:
        """Get list of users/agents"""
        try:
            query = """
                SELECT 
                    u.UserID, u.UserCode, u.UserName, u.InitialPrefix,
                    u.Email, u.Phone, u.IsActive, u.CreatedDate, u.ModifiedDate,
                    ut.UserTypeID, ut.TypeCode, ut.TypeName, ut.Description, ut.Industry
                FROM Users u
                INNER JOIN UserTypes ut ON u.UserTypeID = ut.UserTypeID
                WHERE 1=1
            """
            
            params = []
            
            if user_type:
                query += " AND ut.TypeCode = ?"
                params.append(user_type)
            
            if is_active is not None:
                query += " AND u.IsActive = ?"
                params.append(1 if is_active else 0)
            
            query += " ORDER BY u.UserName"
            
            results = await db_manager.execute_query(query, tuple(params) if params else None)
            
            return [
                UserResponse(
                    user_id=row['UserID'],
                    user_code=row['UserCode'],
                    user_name=row['UserName'],
                    email=row['Email'],
                    phone=row['Phone'],
                    is_active=bool(row['IsActive']),
                    user_type={
                        'user_type_id': row['UserTypeID'],
                        'type_code': row['TypeCode'],
                        'type_name': row['TypeName'],
                        'description': row['Description'],
                        'industry': row['Industry']
                    },
                    initial_prefix=row['InitialPrefix'],
                    created_date=row['CreatedDate'],
                    modified_date=row['ModifiedDate']
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            raise

    async def get_customers(self, is_active: bool = True) -> List[CustomerResponse]:
        """Get list of customers"""
        try:
            query = """
                SELECT 
                    c.CustomerID, c.CustomerCode, c.BusinessName, c.RFC,
                    c.CreditEnabled, c.CreditLimit, c.PaymentTerms,
                    c.IsActive, c.CreatedDate, c.ModifiedDate,
                    ut.UserTypeID, ut.TypeCode, ut.TypeName, ut.Description, ut.Industry
                FROM Customers c
                LEFT JOIN UserTypes ut ON c.CustomerTypeID = ut.UserTypeID
                WHERE 1=1
            """
            
            params = []
            
            if is_active is not None:
                query += " AND c.IsActive = ?"
                params.append(1 if is_active else 0)
            
            query += " ORDER BY c.BusinessName"
            
            results = await db_manager.execute_query(query, tuple(params) if params else None)
            
            return [
                CustomerResponse(
                    customer_id=row['CustomerID'],
                    customer_code=row['CustomerCode'],
                    business_name=row['BusinessName'],
                    rfc=row['RFC'],
                    credit_enabled=bool(row['CreditEnabled']),
                    credit_limit=float(row['CreditLimit']) if row['CreditLimit'] else 0,
                    payment_terms=row['PaymentTerms'],
                    is_active=bool(row['IsActive']),
                    customer_type={
                        'user_type_id': row['UserTypeID'],
                        'type_code': row['TypeCode'],
                        'type_name': row['TypeName'],
                        'description': row['Description'],
                        'industry': row['Industry']
                    } if row['UserTypeID'] else None,
                    created_date=row['CreatedDate'],
                    modified_date=row['ModifiedDate']
                )
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            raise