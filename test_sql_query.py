#!/usr/bin/env python3
"""
Test script to validate SQL query results against reference data

This script:
1. Connects to the database using the same configuration as the Flask app
2. Runs the current get_ventas_por_periodo query
3. Outputs results in the same format as reference data
4. Compares sample months to identify discrepancies
"""

import sys
import os
import pandas as pd
from datetime import datetime
import traceback

# Add the project root to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.reportes import ReporteVentas
from config.database import DatabaseConfig

def format_number(value):
    """Format numbers to match reference data format"""
    if pd.isna(value) or value is None:
        return "0.0"
    return f"{float(value):.6f}".rstrip('0').rstrip('.')

def print_header():
    """Print script header information"""
    print("=" * 80)
    print("SQL Query Validation Test Script")
    print("=" * 80)
    print(f"Test run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_query_results(df):
    """Print query results in reference data format"""
    print("Current Query Results:")
    print("-" * 50)
    print("Year\tMonth\tKilosTotales\t\tToneladasTotales")
    print("-" * 50)
    
    if df.empty:
        print("No results found from query")
        return
    
    for _, row in df.iterrows():
        year = int(row['Anio'])
        month = int(row['Mes'])
        kilos = format_number(row['KilosTotales'])
        toneladas = format_number(row['ToneladasTotales'])
        print(f"{year}\t{month}\t{kilos}\t\t{toneladas}")

def compare_with_reference_data(df):
    """Compare results with known reference data samples"""
    print("\n" + "=" * 80)
    print("COMPARISON WITH REFERENCE DATA")
    print("=" * 80)
    
    # Reference data samples (based on user's example)
    reference_samples = [
        {'year': 2018, 'month': 1, 'kilos': 18901903.94799999, 'toneladas': 18901.903947999992},
        {'year': 2018, 'month': 2, 'kilos': 15651880.668, 'toneladas': 15651.880668},
        # Add more reference samples as provided by user
    ]
    
    print("Reference Data Samples:")
    print("-" * 50)
    print("Year\tMonth\tKilosTotales\t\tToneladasTotales")
    print("-" * 50)
    for ref in reference_samples:
        print(f"{ref['year']}\t{ref['month']}\t{format_number(ref['kilos'])}\t\t{format_number(ref['toneladas'])}")
    
    print("\nComparison Results:")
    print("-" * 50)
    
    discrepancies_found = False
    
    for ref in reference_samples:
        # Find matching row in current results
        matching_row = df[(df['Anio'] == ref['year']) & (df['Mes'] == ref['month'])]
        
        if matching_row.empty:
            print(f"❌ MISSING: {ref['year']}-{ref['month']:02d} - Expected data but found none in current query")
            discrepancies_found = True
        else:
            row = matching_row.iloc[0]
            current_kilos = float(row['KilosTotales'])
            current_toneladas = float(row['ToneladasTotales'])
            
            # Compare with tolerance for floating point precision
            kilos_diff = abs(current_kilos - ref['kilos'])
            toneladas_diff = abs(current_toneladas - ref['toneladas'])
            
            # Set tolerance thresholds
            kilos_tolerance = ref['kilos'] * 0.001  # 0.1% tolerance
            toneladas_tolerance = ref['toneladas'] * 0.001  # 0.1% tolerance
            
            if kilos_diff > kilos_tolerance or toneladas_diff > toneladas_tolerance:
                print(f"❌ MISMATCH: {ref['year']}-{ref['month']:02d}")
                print(f"   Expected Kilos: {format_number(ref['kilos'])}")
                print(f"   Current Kilos:  {format_number(current_kilos)}")
                print(f"   Difference:     {format_number(kilos_diff)}")
                print(f"   Expected Tons:  {format_number(ref['toneladas'])}")
                print(f"   Current Tons:   {format_number(current_toneladas)}")
                print(f"   Difference:     {format_number(toneladas_diff)}")
                discrepancies_found = True
            else:
                print(f"✅ MATCH: {ref['year']}-{ref['month']:02d} - Values match within tolerance")
    
    if not discrepancies_found and len(reference_samples) > 0:
        print("\n🎉 All sample comparisons match!")
    elif len(reference_samples) == 0:
        print("\n⚠️  No reference data provided for comparison")
    
    return discrepancies_found

def analyze_potential_issues(df):
    """Analyze potential issues in the current query"""
    print("\n" + "=" * 80)
    print("POTENTIAL ISSUES ANALYSIS")
    print("=" * 80)
    
    issues = []
    
    # Check for zero values
    zero_kilos = df[df['KilosTotales'] == 0]
    if not zero_kilos.empty:
        issues.append(f"Found {len(zero_kilos)} month(s) with zero KilosTotales")
    
    # Check for inconsistent Kilos to Toneladas conversion
    inconsistent = df[df['ToneladasTotales'] != (df['KilosTotales'] / 1000.0)]
    if not inconsistent.empty:
        issues.append(f"Found {len(inconsistent)} month(s) with inconsistent Kilos/Toneladas conversion")
    
    # Check for unusually high or low values
    if not df.empty:
        mean_kilos = df['KilosTotales'].mean()
        std_kilos = df['KilosTotales'].std()
        outliers = df[(df['KilosTotales'] > mean_kilos + 3 * std_kilos) | 
                     (df['KilosTotales'] < mean_kilos - 3 * std_kilos)]
        if not outliers.empty:
            issues.append(f"Found {len(outliers)} month(s) with outlier values (>3 std deviations)")
    
    # Check date range coverage
    if not df.empty:
        min_year = df['Anio'].min()
        max_year = df['Anio'].max()
        expected_months = (max_year - min_year + 1) * 12
        actual_months = len(df)
        coverage_pct = (actual_months / expected_months) * 100 if expected_months > 0 else 0
        
        if coverage_pct < 80:
            issues.append(f"Date coverage is only {coverage_pct:.1f}% ({actual_months}/{expected_months} months)")
    
    if issues:
        print("Potential Issues Found:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        print("\nPossible Causes:")
        print("- Date filtering excluding some periods")
        print("- Product filtering too restrictive (PRODUCTOS_VALIDOS list)")
        print("- Document type filtering (CIDDOCUMENTODE = 3 or 4)")
        print("- Module filtering (CMODULO = 1)")
        print("- Exclusion of products with CIDDOCUMENTODE = 5 or 6")
        print("- Product name pattern matching in CASE statements")
        print("- Missing or incorrect JOIN conditions")
        
    else:
        print("✅ No obvious issues detected in the data")

def print_data_summary(df):
    """Print summary statistics of the data"""
    print("\n" + "=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    
    if df.empty:
        print("No data returned from query")
        return
    
    print(f"Total months with data: {len(df)}")
    print(f"Date range: {df['Anio'].min()}-{df['Mes'].min():02d} to {df['Anio'].max()}-{df['Mes'].max():02d}")
    print(f"Total Kilos across all periods: {format_number(df['KilosTotales'].sum())}")
    print(f"Total Toneladas across all periods: {format_number(df['ToneladasTotales'].sum())}")
    print(f"Average monthly Kilos: {format_number(df['KilosTotales'].mean())}")
    print(f"Average monthly Toneladas: {format_number(df['ToneladasTotales'].mean())}")
    
    # Show top 5 months by volume
    top_months = df.nlargest(5, 'KilosTotales')
    print(f"\nTop 5 months by volume:")
    for _, row in top_months.iterrows():
        print(f"  {int(row['Anio'])}-{int(row['Mes']):02d}: {format_number(row['KilosTotales'])} kg")

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        db = DatabaseConfig()
        conn = db.get_connection()
        print("✅ Database connection successful")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print_header()
    
    # Test database connection
    if not test_database_connection():
        return
    
    print("\nExecuting current SQL query...")
    print("-" * 50)
    
    try:
        # Create report instance
        reporte = ReporteVentas()
        
        # Run the query (no date filters to get all data)
        df = reporte.get_ventas_por_periodo()
        
        print(f"Query executed successfully. Found {len(df)} rows.")
        print()
        
        # Print results
        print_query_results(df)
        
        # Print summary
        print_data_summary(df)
        
        # Compare with reference data
        discrepancies_found = compare_with_reference_data(df)
        
        # Analyze potential issues
        analyze_potential_issues(df)
        
        print("\n" + "=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)
        
        if discrepancies_found:
            print("⚠️  Discrepancies found between current query and reference data")
            print("   Please review the analysis above and consider:")
            print("   1. Checking the product weight conversion logic")
            print("   2. Verifying document type filtering")
            print("   3. Reviewing date range handling")
            print("   4. Confirming product exclusion rules")
        else:
            print("✅ Query validation completed successfully")
        
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
        print("\nFull error traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main()