"""
Sales service for managing sales documents with normalized data
"""

import logging
from typing import List, Optional
from datetime import datetime, date
from config.database import db_manager
from schemas.sales import (
    SalesDocumentResponse, SalesDocumentCreate, DocumentDetailCreate,
    SalesDocumentSearchResponse, SalesProfitabilityResponse
)

logger = logging.getLogger(__name__)

class SalesService:
    """Service for managing sales documents"""
    
    async def get_sales_documents(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        customer_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[SalesDocumentResponse]:
        """Get sales documents with filters"""
        try:
            # Use the SearchSalesDocuments stored procedure
            procedure_params = (
                start_date, end_date, customer_id, agent_id, status, 
                document_type, None, None, None, limit, (offset // limit) + 1
            )
            
            results = await db_manager.execute_procedure("SearchSalesDocuments", procedure_params)
            
            # The procedure returns two result sets: documents and total count
            documents_data = results[0] if isinstance(results, list) and len(results) > 0 else []
            
            return [self._map_sales_document(row) for row in documents_data]
            
        except Exception as e:
            logger.error(f"Error getting sales documents: {e}")
            raise

    async def get_sales_document(self, document_id: int) -> Optional[SalesDocumentResponse]:
        """Get specific sales document with details"""
        try:
            # Use the GetSalesDocument stored procedure
            results = await db_manager.execute_procedure("GetSalesDocument", (document_id,))
            
            if not results or len(results) < 2:
                return None
            
            # First result set is document header, second is details
            document_data = results[0][0] if results[0] else None
            details_data = results[1] if len(results) > 1 else []
            
            if not document_data:
                return None
                
            return self._map_sales_document_with_details(document_data, details_data)
            
        except Exception as e:
            logger.error(f"Error getting sales document {document_id}: {e}")
            raise

    async def create_sales_document(self, document_data: SalesDocumentCreate) -> SalesDocumentResponse:
        """Create new sales document"""
        try:
            # Use the CreateSalesDocument stored procedure
            procedure_params = (
                document_data.document_type,
                document_data.customer_id,
                document_data.agent_id,
                document_data.document_date,
                document_data.notes
            )
            
            # This procedure should return the new document ID
            results = await db_manager.execute_procedure("CreateSalesDocument", procedure_params)
            
            # Assuming the procedure returns the document ID
            if results and len(results) > 0:
                document_id = results[0].get('DocumentID') if isinstance(results[0], dict) else results[0][0]
                return await self.get_sales_document(document_id)
            else:
                raise Exception("Failed to create sales document")
                
        except Exception as e:
            logger.error(f"Error creating sales document: {e}")
            raise

    async def add_product_to_document(self, document_id: int, detail_data: DocumentDetailCreate) -> bool:
        """Add product to sales document"""
        try:
            # Use the AddProductToDocument stored procedure
            procedure_params = (
                document_id,
                detail_data.product_id,
                detail_data.quantity,
                detail_data.unit_price,
                detail_data.discount_percentage,
                detail_data.notes
            )
            
            await db_manager.execute_procedure("AddProductToDocument", procedure_params)
            return True
            
        except Exception as e:
            logger.error(f"Error adding product to document {document_id}: {e}")
            raise

    async def change_document_status(
        self, 
        document_id: int, 
        new_status: str, 
        user_id: int, 
        notes: Optional[str] = None
    ) -> bool:
        """Change document status"""
        try:
            # Use the ChangeDocumentStatus stored procedure
            procedure_params = (document_id, new_status, user_id, notes)
            
            await db_manager.execute_procedure("ChangeDocumentStatus", procedure_params)
            return True
            
        except Exception as e:
            logger.error(f"Error changing document status {document_id}: {e}")
            raise

    def _map_sales_document(self, row: dict) -> SalesDocumentResponse:
        """Map database row to SalesDocumentResponse"""
        return SalesDocumentResponse(
            document_id=row['DocumentID'],
            document_code=row['DocumentCode'],
            document_type=row['DocumentType'],
            customer_id=row['CustomerID'],
            customer_name=row['CustomerName'],
            agent_id=row['AgentID'],
            agent_name=row['AgentName'],
            document_date=row['DocumentDate'],
            status=row['Status'],
            subtotal=row['Subtotal'],
            tax_amount=row['TaxAmount'],
            discount_amount=row['DiscountAmount'],
            total=row['Total'],
            margin=row['Margin'],
            margin_percentage=row['MarginPercentage'],
            profit_per_kg=row['ProfitPerKg'],
            total_quantity=row['TotalQuantity'],
            notes=row.get('Notes'),
            created_date=row['CreatedDate'],
            modified_date=row['ModifiedDate'],
            details=[]  # Will be populated separately
        )

    def _map_sales_document_with_details(self, document_row: dict, details_rows: List[dict]) -> SalesDocumentResponse:
        """Map document with details to response schema"""
        from schemas.sales import DocumentDetailResponse
        
        # Map the main document
        document = self._map_sales_document(document_row)
        
        # Map the details
        details = []
        for detail_row in details_rows:
            detail = DocumentDetailResponse(
                detail_id=detail_row['DetailID'],
                document_id=detail_row['DocumentID'],
                product_id=detail_row['ProductID'],
                product_code=detail_row['ProductCode'],
                product_name=detail_row['ProductName'],
                category_name=detail_row.get('CategoryName', ''),
                quantity=detail_row['Quantity'],
                unit_price=detail_row['UnitPrice'],
                discount_percentage=detail_row['DiscountPercentage'],
                line_total=detail_row['LineTotal'],
                cost_price=detail_row['CostPrice'],
                margin=detail_row['Margin'],
                margin_percentage=detail_row['MarginPercentage'],
                profit_per_kg=detail_row['ProfitPerKg'],
                notes=detail_row.get('Notes')
            )
            details.append(detail)
        
        document.details = details
        return document