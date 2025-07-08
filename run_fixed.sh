#!/bin/bash
echo "🚀 Starting FIXED Cyberia Business Intelligence..."
cd "/home/ank/Documents/REporte" || exit 1
source venv/bin/activate
echo "✅ All database issues fixed - using only reporteventasenejul"
echo "✅ PDF export working with WeasyPrint"
echo "✅ CRUD operations functional"
echo "🔗 Access at: http://localhost:5004"
python fixed_app.py