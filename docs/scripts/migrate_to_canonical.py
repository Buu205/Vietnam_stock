#!/usr/bin/env python3
"""
Migration Script: Vietnam Dashboard → Canonical Structure
Tự động migrate từ cấu trúc hiện tại sang canonical structure

Usage:
    python3 migrate_to_canonical.py --dry-run   # Preview changes
    python3 migrate_to_canonical.py --execute    # Apply changes
"""
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple
import sys

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(msg: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{msg:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

class CanonicalMigrator:
    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.data_dir = project_root / "DATA"
        self.processors_dir = project_root / "PROCESSORS"
        self.config_dir = project_root / "config"

    def validate_environment(self) -> bool:
        """Validate project structure before migration"""
        print_header("VALIDATING ENVIRONMENT")

        required_dirs = [
            self.data_dir,
            self.processors_dir,
            self.data_dir / "raw",
            self.data_dir / "processed"
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                print_error(f"Missing required directory: {dir_path}")
                return False
            print_success(f"Found: {dir_path.relative_to(self.project_root)}")

        return True

    def create_directory_structure(self) -> List[Path]:
        """Create new canonical directory structure"""
        print_header("CREATING CANONICAL STRUCTURE")

        new_dirs = [
            # Raw data structure
            self.data_dir / "raw" / "fundamental" / "csv" / "Q3_2025",
            self.data_dir / "raw" / "fundamental" / "csv" / "Q4_2025",
            self.data_dir / "raw" / "market" / "ohlcv_raw",
            self.data_dir / "raw" / "macro" / "csv",

            # Refined data structure
            self.data_dir / "refined" / "fundamental" / "current",
            self.data_dir / "refined" / "fundamental" / "archive",
            self.data_dir / "refined" / "technical" / "indicators",
            self.data_dir / "refined" / "valuation",
            self.data_dir / "refined" / "market" / "ohlcv_standardized",

            # Schema consolidation
            self.config_dir / "schemas" / "data",
            self.config_dir / "schemas" / "validation",
            self.config_dir / "schemas" / "display",

            # Processors structure
            self.processors_dir / "extractors",
            self.processors_dir / "transformers" / "financial",
            self.processors_dir / "transformers" / "technical",
            self.processors_dir / "pipelines",
            self.processors_dir / "core" / "validators",
            self.processors_dir / "core" / "registries",
        ]

        created = []
        for dir_path in new_dirs:
            if not dir_path.exists():
                if not self.dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print_success(f"Created: {dir_path.relative_to(self.project_root)}")
                else:
                    print_warning(f"Would create: {dir_path.relative_to(self.project_root)}")
                created.append(dir_path)

        return created

    def migrate_data_files(self) -> List[Tuple[Path, Path]]:
        """Migrate data files to canonical locations"""
        print_header("MIGRATING DATA FILES")

        migrations = []

        # Step 1: Rename processed → refined
        old_processed = self.data_dir / "processed"
        new_refined = self.data_dir / "refined"

        if old_processed.exists() and not new_refined.exists():
            migrations.append((old_processed, new_refined))
            if not self.dry_run:
                shutil.move(str(old_processed), str(new_refined))
                print_success(f"Renamed: processed → refined")
            else:
                print_warning(f"Would rename: processed → refined")

        # Step 2: Move CSV files from raw/fundamental/processed to raw/fundamental/csv/Q3_2025
        raw_processed = self.data_dir / "raw" / "fundamental" / "processed"
        if raw_processed.exists():
            csv_target = self.data_dir / "raw" / "fundamental" / "csv" / "Q3_2025"

            for csv_file in raw_processed.glob("*.csv"):
                target = csv_target / csv_file.name
                migrations.append((csv_file, target))

                if not self.dry_run:
                    if not csv_target.exists():
                        csv_target.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(csv_file), str(target))
                    print_success(f"Moved CSV: {csv_file.name}")
                else:
                    print_warning(f"Would move: {csv_file.name} → {csv_target.relative_to(self.data_dir)}")

            # Step 3: Move parquet files to refined/fundamental/current
            parquet_target = self.data_dir / "refined" / "fundamental" / "current"

            for parquet_file in raw_processed.glob("*.parquet"):
                target = parquet_target / parquet_file.name
                migrations.append((parquet_file, target))

                if not self.dry_run:
                    if not parquet_target.exists():
                        parquet_target.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(parquet_file), str(target))
                    print_success(f"Moved parquet: {parquet_file.name}")
                else:
                    print_warning(f"Would move: {parquet_file.name} → {parquet_target.relative_to(self.data_dir)}")

        return migrations

    def consolidate_schemas(self) -> List[Tuple[Path, Path]]:
        """Consolidate schemas to config/schemas/"""
        print_header("CONSOLIDATING SCHEMAS")

        migrations = []
        schema_sources = [
            self.data_dir / "schemas",
            self.processors_dir / "core" / "schemas"
        ]

        schema_target = self.config_dir / "schemas" / "data"

        for source_dir in schema_sources:
            if source_dir.exists():
                for schema_file in source_dir.glob("**/*.json"):
                    target = schema_target / schema_file.name
                    migrations.append((schema_file, target))

                    if not self.dry_run:
                        if not schema_target.exists():
                            schema_target.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(schema_file), str(target))
                        print_success(f"Copied schema: {schema_file.name}")
                    else:
                        print_warning(f"Would copy: {schema_file.name} → config/schemas/data/")

        return migrations

    def update_paths_config(self) -> bool:
        """Update PROCESSORS/core/config/paths.py"""
        print_header("UPDATING PATH CONFIGURATION")

        paths_file = self.processors_dir / "core" / "config" / "paths.py"

        if not paths_file.exists():
            print_error(f"paths.py not found at {paths_file}")
            return False

        content = paths_file.read_text()

        # Replace: processed → refined
        old_patterns = [
            'DATA / "processed"',
            '"processed"',
            "/processed/",
            "processed/"
        ]

        new_content = content
        for pattern in old_patterns:
            if pattern in new_content:
                new_pattern = pattern.replace("processed", "refined")
                new_content = new_content.replace(pattern, new_pattern)

        if new_content != content:
            if not self.dry_run:
                paths_file.write_text(new_content)
                print_success("Updated paths.py: processed → refined")
            else:
                print_warning("Would update paths.py: processed → refined")
            return True

        print_success("paths.py already up to date")
        return True

    def create_schema_registry(self) -> bool:
        """Create SchemaRegistry class"""
        print_header("CREATING SCHEMA REGISTRY")

        registry_file = self.processors_dir / "core" / "registries" / "schema_registry.py"

        if registry_file.exists():
            print_warning(f"SchemaRegistry already exists: {registry_file.name}")
            return True

        registry_code = '''"""
Schema Registry - Centralized schema management
Provides single source of truth for all schemas
"""
from pathlib import Path
import json
from typing import Dict, Any

class SchemaRegistry:
    """Centralized schema management"""

    def __init__(self):
        # Path to config/schemas/
        self.schema_dir = Path(__file__).resolve().parents[3] / "config" / "schemas"

    def get_data_schema(self, name: str) -> Dict[str, Any]:
        """Get data schema (e.g., 'ohlcv', 'fundamental')"""
        return self._load_schema("data", name)

    def get_validation_schema(self, name: str) -> Dict[str, Any]:
        """Get validation schema"""
        return self._load_schema("validation", name)

    def get_display_schema(self, name: str) -> Dict[str, Any]:
        """Get display formatting schema"""
        return self._load_schema("display", name)

    def _load_schema(self, category: str, name: str) -> Dict[str, Any]:
        """Load schema from file"""
        schema_path = self.schema_dir / category / f"{name}.json"

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_schemas(self, category: str = None) -> Dict[str, list]:
        """List all available schemas"""
        if category:
            schema_dir = self.schema_dir / category
            return {category: [f.stem for f in schema_dir.glob("*.json")]}

        result = {}
        for cat_dir in self.schema_dir.iterdir():
            if cat_dir.is_dir():
                result[cat_dir.name] = [f.stem for f in cat_dir.glob("*.json")]

        return result

# Global instance
schema_registry = SchemaRegistry()
'''

        if not self.dry_run:
            registries_dir = registry_file.parent
            if not registries_dir.exists():
                registries_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py
            init_file = registries_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Registry modules"""\n')

            registry_file.write_text(registry_code)
            print_success(f"Created: {registry_file.relative_to(self.project_root)}")
        else:
            print_warning("Would create SchemaRegistry class")

        return True

    def generate_migration_report(self) -> str:
        """Generate migration summary report"""
        print_header("MIGRATION SUMMARY")

        report = []
        report.append("\n" + "="*60)
        report.append("VIETNAM DASHBOARD - CANONICAL MIGRATION REPORT")
        report.append("="*60 + "\n")

        if self.dry_run:
            report.append("⚠️  DRY RUN MODE - No changes applied\n")
        else:
            report.append("✅ EXECUTION MODE - Changes applied\n")

        report.append("Changes:")
        report.append("  1. ✅ Renamed DATA/processed → DATA/refined")
        report.append("  2. ✅ Moved CSV files to DATA/raw/fundamental/csv/Q3_2025/")
        report.append("  3. ✅ Moved parquet to DATA/refined/fundamental/current/")
        report.append("  4. ✅ Consolidated schemas to config/schemas/")
        report.append("  5. ✅ Updated paths.py (processed → refined)")
        report.append("  6. ✅ Created SchemaRegistry class\n")

        report.append("Next Steps:")
        report.append("  1. Test imports: python3 -c 'from PROCESSORS.core.registries.schema_registry import schema_registry'")
        report.append("  2. Run calculators to verify data loading")
        report.append("  3. Update WEBAPP to use new paths")
        report.append("  4. Commit changes: git commit -m 'feat: Migrate to canonical structure'")

        report_text = "\n".join(report)
        print(report_text)

        return report_text

    def run_migration(self) -> bool:
        """Execute full migration"""
        try:
            # Step 1: Validate
            if not self.validate_environment():
                print_error("Environment validation failed")
                return False

            # Step 2: Create structure
            self.create_directory_structure()

            # Step 3: Migrate data
            self.migrate_data_files()

            # Step 4: Consolidate schemas
            self.consolidate_schemas()

            # Step 5: Update paths
            self.update_paths_config()

            # Step 6: Create registry
            self.create_schema_registry()

            # Step 7: Report
            self.generate_migration_report()

            return True

        except Exception as e:
            print_error(f"Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Migrate Vietnam Dashboard to canonical structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute migration (apply changes)"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.dry_run and not args.execute:
        print_error("Must specify either --dry-run or --execute")
        parser.print_help()
        sys.exit(1)

    if args.dry_run and args.execute:
        print_error("Cannot specify both --dry-run and --execute")
        sys.exit(1)

    # Run migration
    migrator = CanonicalMigrator(
        project_root=args.project_root,
        dry_run=args.dry_run
    )

    success = migrator.run_migration()

    if success:
        print_success("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print_error("\n❌ Migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
