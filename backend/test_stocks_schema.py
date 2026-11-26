#!/usr/bin/env python3
"""
Test stocks table and association schema.

This script validates:
1. Stocks table exists and has correct schema
2. content_stock_mentions junction table exists
3. Relationships work correctly
4. Can insert and query stocks
5. Can associate stocks with raw_content

Usage: python test_stocks_schema.py
"""
import sys
from datetime import datetime
from sqlalchemy import inspect

from app.core.db import SessionLocal, engine
from app.models.sentiment import Stock, ContentStockMention, RawContent, SourceType

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_section(title):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗{RESET} {message}")


def print_info(message):
    """Print info message"""
    print(f"  {message}")


def test_tables_exist():
    """Test that stocks and content_stock_mentions tables exist"""
    print_section("1. Testing Table Existence")

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = ['stocks', 'content_stock_mentions', 'raw_content']
    results = {}

    for table in required_tables:
        if table in tables:
            print_success(f"Table '{table}' exists")
            results[table] = True
        else:
            print_error(f"Table '{table}' not found")
            results[table] = False

    return all(results.values())


def test_stocks_schema():
    """Test stocks table schema"""
    print_section("2. Testing Stocks Table Schema")

    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('stocks')}

    required_columns = {
        'id': 'INTEGER',
        'symbol': 'VARCHAR',
        'company_name': 'VARCHAR',
        'sector': 'VARCHAR',
        'exchange': 'VARCHAR',
        'is_active': 'BOOLEAN',
        'last_updated': 'TIMESTAMP',
        'created_at': 'TIMESTAMP'
    }

    all_good = True

    for col_name, expected_type in required_columns.items():
        if col_name in columns:
            actual_type = str(columns[col_name]['type']).upper()
            if expected_type in actual_type or actual_type.startswith(expected_type):
                print_success(f"Column '{col_name}' exists with type {actual_type}")
            else:
                print_error(f"Column '{col_name}' has wrong type: {actual_type} (expected {expected_type})")
                all_good = False
        else:
            print_error(f"Column '{col_name}' missing")
            all_good = False

    # Check indexes
    indexes = inspector.get_indexes('stocks')
    print_info(f"\nIndexes on stocks table: {len(indexes)}")
    for idx in indexes:
        print_info(f"  - {idx['name']}: {idx['column_names']}")

    # Check constraints
    pk = inspector.get_pk_constraint('stocks')
    print_info(f"\nPrimary key: {pk['constrained_columns']}")

    return all_good


def test_junction_table_schema():
    """Test content_stock_mentions junction table schema"""
    print_section("3. Testing content_stock_mentions Junction Table")

    inspector = inspect(engine)
    columns = {col['name']: col for col in inspector.get_columns('content_stock_mentions')}

    required_columns = {
        'id': 'BIGINT',
        'content_id': 'BIGINT',
        'stock_id': 'INTEGER',
        'mention_type': 'VARCHAR',
        'confidence': 'FLOAT',
        'created_at': 'TIMESTAMP'
    }

    all_good = True

    for col_name, expected_type in required_columns.items():
        if col_name in columns:
            actual_type = str(columns[col_name]['type']).upper()
            # Handle different type representations
            if any(t in actual_type for t in [expected_type, expected_type.replace('FLOAT', 'DOUBLE')]):
                print_success(f"Column '{col_name}' exists with type {actual_type}")
            else:
                print_error(f"Column '{col_name}' has wrong type: {actual_type} (expected {expected_type})")
                all_good = False
        else:
            print_error(f"Column '{col_name}' missing")
            all_good = False

    # Check foreign keys
    fks = inspector.get_foreign_keys('content_stock_mentions')
    print_info(f"\nForeign keys: {len(fks)}")
    for fk in fks:
        print_info(f"  - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")

    # Check indexes
    indexes = inspector.get_indexes('content_stock_mentions')
    print_info(f"\nIndexes: {len(indexes)}")
    for idx in indexes:
        unique = " (unique)" if idx.get('unique') else ""
        print_info(f"  - {idx['name']}: {idx['column_names']}{unique}")

    return all_good


def test_crud_operations():
    """Test CRUD operations on stocks table"""
    print_section("4. Testing CRUD Operations")

    db = SessionLocal()

    try:
        # Clean up test data
        db.query(Stock).filter(Stock.symbol == 'TEST').delete()
        db.commit()

        # CREATE
        test_stock = Stock(
            symbol='TEST',
            company_name='Test Company Inc.',
            sector='Technology',
            exchange='NASDAQ',
            is_active=True
        )
        db.add(test_stock)
        db.commit()
        db.refresh(test_stock)

        print_success(f"Created stock: {test_stock.symbol} (ID: {test_stock.id})")
        print_info(f"  Company: {test_stock.company_name}")
        print_info(f"  Sector: {test_stock.sector}")

        # READ
        found = db.query(Stock).filter(Stock.symbol == 'TEST').first()
        if found and found.id == test_stock.id:
            print_success("Read stock successfully")
        else:
            print_error("Failed to read stock")
            return False

        # UPDATE
        found.company_name = 'Updated Test Company'
        db.commit()
        db.refresh(found)

        if found.company_name == 'Updated Test Company':
            print_success("Updated stock successfully")
        else:
            print_error("Failed to update stock")
            return False

        # COUNT
        count = db.query(Stock).count()
        print_success(f"Total stocks in database: {count}")

        # DELETE (cleanup)
        db.delete(test_stock)
        db.commit()
        print_success("Deleted test stock")

        return True

    except Exception as e:
        print_error(f"CRUD operations failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_associations():
    """Test associations between raw_content and stocks"""
    print_section("5. Testing Content-Stock Associations")

    db = SessionLocal()

    try:
        # Create test stock
        test_stock = Stock(
            symbol='ASSOC',
            company_name='Association Test Inc.',
            sector='Testing'
        )
        db.add(test_stock)
        db.commit()
        db.refresh(test_stock)

        print_success(f"Created test stock: {test_stock.symbol} (ID: {test_stock.id})")

        # Create test content
        test_content = RawContent(
            source=SourceType.reddit,
            external_id='test_assoc_123',
            source_identifier='r/test',
            content_type='post',
            title='Test post mentioning $ASSOC',
            body='This is a test post about $ASSOC stock',
            author='test_user',
            collected_at=datetime.utcnow(),
            content_created_at=datetime.utcnow(),
            processed=False
        )
        db.add(test_content)
        db.commit()
        db.refresh(test_content)

        print_success(f"Created test content: {test_content.external_id} (ID: {test_content.id})")

        # Create association
        mention = ContentStockMention(
            content_id=test_content.id,
            stock_id=test_stock.id,
            mention_type='cashtag',
            confidence=1.0
        )
        db.add(mention)
        db.commit()
        db.refresh(mention)

        print_success(f"Created association: content {test_content.id} → stock {test_stock.id}")

        # Query association
        found_mention = db.query(ContentStockMention).filter(
            ContentStockMention.content_id == test_content.id,
            ContentStockMention.stock_id == test_stock.id
        ).first()

        if found_mention:
            print_success("Retrieved association successfully")
            print_info(f"  Mention type: {found_mention.mention_type}")
            print_info(f"  Confidence: {found_mention.confidence}")
        else:
            print_error("Failed to retrieve association")
            return False

        # Test unique constraint (should fail if we try to create duplicate)
        try:
            duplicate = ContentStockMention(
                content_id=test_content.id,
                stock_id=test_stock.id,
                mention_type='company_name'
            )
            db.add(duplicate)
            db.commit()
            print_error("Unique constraint not working (allowed duplicate)")
            return False
        except Exception:
            db.rollback()
            print_success("Unique constraint working (prevented duplicate)")

        # Cleanup
        db.delete(mention)
        db.delete(test_content)
        db.delete(test_stock)
        db.commit()
        print_success("Cleaned up test data")

        return True

    except Exception as e:
        print_error(f"Association test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def show_existing_stocks():
    """Show existing stocks in database"""
    print_section("6. Existing Stocks in Database")

    db = SessionLocal()

    try:
        stocks = db.query(Stock).order_by(Stock.symbol).limit(20).all()

        if stocks:
            print_info(f"Found {len(stocks)} stocks (showing up to 20):\n")
            for stock in stocks:
                print_info(f"  {stock.symbol:6} - {stock.company_name or 'N/A':40} [{stock.sector or 'N/A'}]")
        else:
            print_info("No stocks in database yet")

        total = db.query(Stock).count()
        print_info(f"\nTotal stocks: {total}")

        db.close()
        return True

    except Exception as e:
        print_error(f"Failed to query stocks: {e}")
        db.close()
        return False


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'*' * 70}")
    print(f"  Stocks Table and Association Schema Test")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"{'*' * 70}{RESET}\n")

    results = []

    # Run tests
    results.append(("Tables Exist", test_tables_exist()))
    results.append(("Stocks Schema", test_stocks_schema()))
    results.append(("Junction Table Schema", test_junction_table_schema()))
    results.append(("CRUD Operations", test_crud_operations()))
    results.append(("Associations", test_associations()))
    results.append(("Show Existing Stocks", show_existing_stocks()))

    # Print summary
    print_section("Test Summary")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        if success:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")

    print(f"\n{BLUE}{'=' * 70}{RESET}")
    if passed == total:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}")
        print(f"\n{GREEN}✓ Stocks schema is working correctly{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}Some tests failed ({passed}/{total}){RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
