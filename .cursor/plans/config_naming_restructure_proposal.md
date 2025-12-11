# CONFIG SYSTEM - ĐỀ XUẤT TÁI CẤU TRÚC TÊN FILE/FOLDER
## Giải quyết vấn đề trùng lặp và nhầm lẫn trong naming

---

**Ngày tạo:** 2025-12-11
**Tác giả:** Claude Code
**Ưu tiên:** HIGH - Cần thực hiện trước khi implement optimization plan
**Thời gian:** 1 ngày

---

## 1. VẤN ĐỀ HIỆN TẠI - NAMING CONFLICTS

### 1.1 Phân tích các trường hợp trùng lặp gây nhầm lẫn

| # | Tên hiện tại | Loại | Vấn đề | Mức độ nghiêm trọng |
|---|--------------|------|--------|---------------------|
| 1 | `schema_registry.py` (file)<br>`schema_registry/` (folder) | File vs Folder | ⚠️ Tên giống hệt nhau, khó phân biệt khi import | 🔴 HIGH |
| 2 | `config/metadata/`<br>`DATA/metadata/` | 2 folders | ⚠️ Cùng tên, chứa cùng loại data (metric_registry.json) | 🔴 HIGH |
| 3 | `metric_registry.json` | Xuất hiện ở 2+ nơi | ⚠️ Không rõ file nào là source of truth | 🔴 HIGH |
| 4 | `registries/` (trong config)<br>Registry classes | Folder vs Concept | ⚠️ "Registries" vừa là folder chứa code, vừa là khái niệm | 🟡 MEDIUM |
| 5 | `schemas/` (legacy)<br>`schema_registry/` (new) | 2 folders cùng mục đích | ⚠️ Chứa cùng loại JSON schemas, gây confusion | 🟡 MEDIUM |

### 1.2 Import confusion examples

```python
# ❌ CONFUSING - Không rõ đang import file hay folder
from config.schema_registry import SchemaRegistry  # File: schema_registry.py
from config.schema_registry import get_core_schema  # ??? Có tồn tại không?

# ❌ CONFUSING - metric_registry ở đâu?
metric_path_1 = "DATA/metadata/metric_registry.json"      # Bản to (770KB)
metric_path_2 = "config/metadata/metric_registry.json"    # Bản nhỏ hay placeholder?

# ❌ CONFUSING - schemas vs schema_registry?
old_path = "config/schemas/data/ohlcv_schema.json"       # Legacy
new_path = "config/schema_registry/domain/technical/..."  # New
```

---

## 2. ĐỀ XUẤT CẤU TRÚC MỚI - CLEAR NAMING

### 2.1 Nguyên tắc đặt tên mới

1. **Descriptive Names** - Tên phải mô tả rõ chức năng
2. **No Overlap** - Không được trùng tên giữa file và folder
3. **Clear Hierarchy** - Cấu trúc thư mục phản ánh mục đích
4. **Single Source** - Mỗi loại data chỉ có 1 location chính thức
5. **Vietnamese-Friendly** - Code có docstrings tiếng Việt

### 2.2 Cấu trúc mới đề xuất

```
config/
├── registry_classes/                    ✅ MỚI: Đổi từ "registries/"
│   ├── __init__.py
│   ├── metric_registry_loader.py       ✅ MỚI: Đổi từ "metric_lookup.py"
│   ├── sector_registry_loader.py       ✅ MỚI: Đổi từ "sector_lookup.py"
│   └── builders/
│       ├── build_metric_registry.py
│       └── build_sector_registry.py
│
├── schema_manager.py                    ✅ MỚI: Đổi từ "schema_registry.py"
│                                        (Singleton class để load schemas)
│
├── schemas/                             ✅ MỚI: Đổi từ "schema_registry/"
│   ├── core/                           (types, entities, mappings)
│   ├── domains/                        ✅ MỚI: Đổi từ "domain/"
│   │   ├── fundamental/
│   │   ├── technical/
│   │   ├── valuation/
│   │   └── unified/
│   └── display/                        (charts, tables, dashboards)
│
├── data_registry/                       ✅ MỚI: Đổi từ "metadata/"
│   ├── metric_registry.json            ✅ PRIMARY SOURCE (copy từ DATA/metadata/)
│   ├── sector_industry_registry.json   ✅ PRIMARY SOURCE
│   └── ticker_details.json
│
├── business_rules/                      ✅ MỚI: Đổi từ "business_logic/"
│   ├── analysis_configs/               ✅ MỚI: Đổi từ "analysis/"
│   ├── decision_rules/                 ✅ MỚI: Đổi từ "decisions/"
│   └── alert_configs/                  ✅ MỚI: Đổi từ "alerts/"
│
├── sector_analysis_config/              ✅ MỚI: Đổi từ "sector_analysis/"
│   ├── __init__.py
│   └── fa_ta_weights_manager.py        ✅ MỚI: Đổi từ "config_manager.py"
│
├── legacy_schemas/                      ✅ MỚI: Đổi từ "schemas/"
│   ├── master_display_config.json      ✅ MỚI: Đổi từ "master_schema.json"
│   └── archived/                       ✅ MỚI: Move old schemas here
│       ├── ohlcv_schema_old.json
│       ├── fundamental_schema_old.json
│       └── technical_schema_old.json
│
└── README_CONFIG_STRUCTURE.md           ✅ MỚI: Tài liệu cấu trúc
```

---

## 3. MAPPING TABLE - TÊN CŨ → TÊN MỚI

### 3.1 Python Files (Classes & Modules)

| Tên cũ | Tên mới | Lý do đổi |
|--------|---------|-----------|
| `schema_registry.py` | `schema_manager.py` | ✅ Tránh trùng với folder `schema_registry/` → `schemas/` |
| `config/registries/metric_lookup.py` | `config/registry_classes/metric_registry_loader.py` | ✅ Tên rõ hơn: "loader" thể hiện chức năng load & lookup |
| `config/registries/sector_lookup.py` | `config/registry_classes/sector_registry_loader.py` | ✅ Consistent với metric_registry_loader |
| `config/sector_analysis/config_manager.py` | `config/sector_analysis_config/fa_ta_weights_manager.py` | ✅ Tên specific hơn: quản lý FA/TA weights |

### 3.2 Folders

| Tên cũ | Tên mới | Lý do đổi |
|--------|---------|-----------|
| `config/registries/` | `config/registry_classes/` | ✅ "Classes" thể hiện đây là Python code, không phải data |
| `config/schema_registry/` | `config/schemas/` | ✅ Ngắn gọn hơn, tránh trùng với `schema_registry.py` → `schema_manager.py` |
| `config/schema_registry/domain/` | `config/schemas/domains/` | ✅ Số nhiều (domains) rõ hơn là chứa nhiều domain |
| `config/metadata/` | `config/data_registry/` | ✅ "Data registry" rõ ràng hơn "metadata" |
| `config/business_logic/` | `config/business_rules/` | ✅ "Rules" dễ hiểu hơn "logic" cho non-technical users |
| `config/business_logic/analysis/` | `config/business_rules/analysis_configs/` | ✅ Thêm "_configs" để rõ đây là config files |
| `config/business_logic/decisions/` | `config/business_rules/decision_rules/` | ✅ Thêm "_rules" để consistent |
| `config/business_logic/alerts/` | `config/business_rules/alert_configs/` | ✅ Thêm "_configs" để consistent |
| `config/sector_analysis/` | `config/sector_analysis_config/` | ✅ Thêm "_config" để rõ đây là config, không phải analyzer |
| `config/schemas/` (legacy) | `config/legacy_schemas/` | ✅ "Legacy" rõ ràng đây là code cũ |
| `config/schemas/data/` | `config/legacy_schemas/archived/` | ✅ "Archived" thể hiện sẽ xóa sau này |

### 3.3 JSON Schema Files

| Tên cũ | Tên mới | Lý do đổi |
|--------|---------|-----------|
| `master_schema.json` | `master_display_config.json` | ✅ "Display config" rõ ràng hơn là dùng cho UI |
| `ohlcv.json` | **XÓA** (duplicate) | ✅ Giữ `ohlcv_schema.json` |
| `config/schemas/data/master_schema.json` | **XÓA** (duplicate) | ✅ Giữ version ở root |

### 3.4 Data Registry Files

| Vị trí cũ | Vị trí mới | Action |
|-----------|------------|--------|
| `DATA/metadata/metric_registry.json` (770KB) | `config/data_registry/metric_registry.json` | ✅ **COPY** từ DATA/ sang config/ |
| `DATA/metadata/sector_industry_registry.json` | `config/data_registry/sector_industry_registry.json` | ✅ **COPY** từ DATA/ sang config/ |
| `config/metadata/ticker_details.json` | `config/data_registry/ticker_details.json` | ✅ **MOVE** (chỉ tồn tại ở config/) |

**Lưu ý quan trọng:**
- `DATA/metadata/` vẫn giữ nguyên để làm backup/rebuild source
- `config/data_registry/` là **PRIMARY SOURCE** cho toàn bộ codebase sử dụng
- Mọi import phải dùng `config/data_registry/`, **KHÔNG** truy cập `DATA/metadata/` trực tiếp

---

## 4. IMPORT PATTERNS - TRƯỚC VÀ SAU

### 4.1 Schema Manager (SchemaRegistry)

**❌ CŨ (confusing):**
```python
from config.schema_registry import SchemaRegistry  # Trùng tên folder
```

**✅ MỚI (clear):**
```python
from config.schema_manager import SchemaManager  # Rõ ràng đây là file schema_manager.py

# Sử dụng
schema_mgr = SchemaManager()
price_formatted = schema_mgr.format_price(25750.5)
```

### 4.2 Metric Registry

**❌ CŨ (confusing):**
```python
from config.registries.metric_lookup import MetricRegistry
# hoặc
from PROCESSORS.core.registries.metric_lookup import MetricRegistry  # Deprecated
```

**✅ MỚI (clear):**
```python
from config.registry_classes.metric_registry_loader import MetricRegistryLoader

# Sử dụng
metric_loader = MetricRegistryLoader()
metric_info = metric_loader.get_metric("CIS_62", "COMPANY")
```

### 4.3 Sector Registry

**❌ CŨ (confusing):**
```python
from config.registries.sector_lookup import SectorRegistry
```

**✅ MỚI (clear):**
```python
from config.registry_classes.sector_registry_loader import SectorRegistryLoader

# Sử dụng
sector_loader = SectorRegistryLoader()
peers = sector_loader.get_peers("ACB")
```

### 4.4 Schema Loading

**❌ CŨ (confusing):**
```python
schema = registry.get_schema('metrics')  # Không rõ loại gì
```

**✅ MỚI (clear):**
```python
schema_mgr = SchemaManager()

# Rõ ràng hơn
fundamental_metrics = schema_mgr.get_domain_schema('fundamental', 'metrics')
chart_config = schema_mgr.get_display_schema('charts')
core_types = schema_mgr.get_core_schema('types')
```

---

## 5. IMPLEMENTATION PLAN

### Phase 0: Backup & Preparation (0.5 ngày)

**Backup toàn bộ config/**
```bash
# Tạo backup
cd /Users/buuphan/Dev/Vietnam_dashboard
cp -r config config_backup_2025_12_11

# Verify backup
ls -la config_backup_2025_12_11/
```

### Phase 1: Rename Folders (0.5 ngày)

**Step 1.1: Rename main directories**
```bash
cd config/

# Rename folders theo thứ tự
mv registries/ registry_classes/
mv schema_registry/ schemas/
mv schemas/ legacy_schemas/  # Đổi cái cũ trước
mv metadata/ data_registry/
mv business_logic/ business_rules/
mv sector_analysis/ sector_analysis_config/
```

**Step 1.2: Rename subdirectories**
```bash
cd config/schemas/  # (mới đổi từ schema_registry/)
mv domain/ domains/  # Số nhiều

cd config/business_rules/  # (mới đổi từ business_logic/)
mv analysis/ analysis_configs/
mv decisions/ decision_rules/
mv alerts/ alert_configs/

cd config/legacy_schemas/  # (mới đổi từ schemas/)
mkdir archived/
mv data/*.json archived/  # Move old schemas
```

### Phase 2: Rename Python Files (0.5 ngày)

```bash
cd config/

# Rename main files
mv schema_registry.py schema_manager.py

cd registry_classes/  # (mới đổi từ registries/)
mv metric_lookup.py metric_registry_loader.py
mv sector_lookup.py sector_registry_loader.py

cd ../sector_analysis_config/  # (mới đổi từ sector_analysis/)
mv config_manager.py fa_ta_weights_manager.py

cd ../legacy_schemas/
mv master_schema.json master_display_config.json
```

### Phase 3: Update Class Names (1 ngày)

**File: `config/schema_manager.py` (cũ: schema_registry.py)**

```python
#!/usr/bin/env python3
"""
Schema Manager - Quản lý tập trung các schemas
==============================================

Lớp Singleton để load và quản lý tất cả schemas trong hệ thống.

Tác giả: Claude Code
Ngày cập nhật: 2025-12-11
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class SchemaManager:
    """
    Schema Manager - Quản lý tập trung schemas

    Lớp Singleton để load và cache schemas từ:
    - config/schemas/ (core, domains, display)
    - config/data_registry/ (metric_registry, sector_registry)
    - config/business_rules/ (analysis, decision, alert configs)
    - config/legacy_schemas/ (backward compatibility)

    Ví dụ sử dụng:
        >>> schema_mgr = SchemaManager()
        >>> price = schema_mgr.format_price(25750.5)  # "25,750.50đ"
        >>> color = schema_mgr.get_color('positive_change')  # "#00C853"
    """
    _instance = None
    _schemas_loaded = False

    def __new__(cls):
        """Đảm bảo chỉ có 1 instance duy nhất (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(SchemaManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Khởi tạo Schema Manager - chỉ load schemas 1 lần duy nhất"""
        if not SchemaManager._schemas_loaded:
            self._load_all_schemas()
            SchemaManager._schemas_loaded = True

    def _load_all_schemas(self):
        """
        Load tất cả schemas từ config/

        Thứ tự ưu tiên:
        1. config/data_registry/ (metric & sector registries)
        2. config/schemas/ (core, domains, display)
        3. config/business_rules/ (analysis, decision, alert)
        4. config/legacy_schemas/ (backward compatibility)
        """
        self.config_dir = Path(__file__).parent

        # Các thư mục schemas
        self.schemas_dir = self.config_dir / "schemas"
        self.data_registry_dir = self.config_dir / "data_registry"
        self.business_rules_dir = self.config_dir / "business_rules"
        self.legacy_schemas_dir = self.config_dir / "legacy_schemas"

        # Load master display config (cũ: master_schema.json)
        master_path = self.legacy_schemas_dir / "master_display_config.json"
        if master_path.exists():
            with open(master_path, 'r', encoding='utf-8') as f:
                self.master_config = json.load(f)

            # Extract các settings thường dùng
            self.app_metadata = self.master_config['app_metadata']
            self.global_settings = self.master_config['global_settings']
            self.theme = self.master_config['theme']
            self.formatting_rules = self.master_config['formatting_rules']
            self.frequency_codes = self.master_config['frequency_codes']
            self.validation_thresholds = self.master_config['validation_thresholds']
            self.entity_types = self.master_config['entity_types']
            self.chart_defaults = self.master_config['chart_defaults']
        else:
            logger.warning("master_display_config.json không tìm thấy, dùng giá trị mặc định")
            self._load_defaults()

        # Cache cho schemas đã load
        self._schema_cache = {}

        logger.info("SchemaManager đã khởi tạo thành công")

    # ... (rest of methods remain same logic, just update docstrings to Vietnamese)

    def format_price(self, value: Union[float, int], include_currency: bool = True) -> str:
        """
        Format giá tiền theo quy tắc định dạng

        Args:
            value: Giá trị cần format
            include_currency: Có hiển thị ký hiệu tiền tệ không

        Returns:
            Chuỗi đã format (vd: "25,750.50đ")

        Ví dụ:
            >>> schema_mgr.format_price(25750.5)
            '25,750.50đ'
            >>> schema_mgr.format_price(25750.5, include_currency=False)
            '25,750.50'
        """
        # ... existing implementation


# Convenience functions cho import trực tiếp
_schema_manager = None

def get_schema_manager() -> SchemaManager:
    """Lấy instance SchemaManager (Singleton)"""
    global _schema_manager
    if _schema_manager is None:
        _schema_manager = SchemaManager()
    return _schema_manager


# Direct access functions với docstrings tiếng Việt
def format_price(value: Union[float, int], include_currency: bool = True) -> str:
    """Format giá tiền sử dụng SchemaManager toàn cục"""
    return get_schema_manager().format_price(value, include_currency)


def format_volume(value: Union[int, float]) -> str:
    """Format khối lượng giao dịch sử dụng SchemaManager toàn cục"""
    return get_schema_manager().format_volume(value)
```

**File: `config/registry_classes/metric_registry_loader.py` (cũ: metric_lookup.py)**

```python
#!/usr/bin/env python3
"""
Metric Registry Loader - Trình load & lookup metric definitions
================================================================

Load và tra cứu nhanh các định nghĩa metric từ metric_registry.json

Tính năng:
- Lấy metric theo code (CIS_62, BBS_100, v.v.)
- Tìm kiếm metric theo tên (Tiếng Việt/Tiếng Anh)
- Lấy công thức calculated metrics
- Validate dependencies

Tác giả: Claude Code
Ngày cập nhật: 2025-12-11
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


def find_project_root() -> Path:
    """Tìm thư mục gốc project (Vietnam_dashboard)"""
    current = Path(__file__).resolve()
    while current.parent != current:
        if current.name in ['Vietnam_dashboard', 'stock_dashboard']:
            return current
        current = current.parent
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = find_project_root()


class MetricRegistryLoader:
    """
    Trình load & lookup nhanh cho metric definitions

    Load từ config/data_registry/metric_registry.json (PRIMARY SOURCE)

    Cung cấp:
    - Raw metric codes từ BSC database (CIS_*, BBS_*, v.v.)
    - Calculated metric formulas (ROE, gross_margin, v.v.)
    - Metric dependencies và validation

    Ví dụ:
        >>> loader = MetricRegistryLoader()
        >>> metric = loader.get_metric("CIS_62", "COMPANY")
        >>> # {'code': 'CIS_62', 'name_vi': 'Lợi nhuận sau thuế...', ...}
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Khởi tạo Metric Registry Loader

        Args:
            registry_path: Đường dẫn đến metric_registry.json (mặc định: auto-detect)
        """
        if registry_path is None:
            # PRIMARY SOURCE: config/data_registry/metric_registry.json
            registry_path = PROJECT_ROOT / "config" / "data_registry" / "metric_registry.json"
        else:
            registry_path = Path(registry_path)

        if not registry_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy metric registry: {registry_path}\n"
                f"Vui lòng chạy: python config/registry_classes/builders/build_metric_registry.py"
            )

        # Load registry
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = json.load(f)

        logger.info(f"Đã load metric registry v{self.registry['version']}")
        logger.info(f"  Tổng entity types: {len(self.registry['entity_types'])}")
        logger.info(f"  Calculated metrics: {len(self.registry['calculated_metrics'])}")

    def get_metric(self, code: str, entity_type: Optional[str] = None) -> Optional[Dict]:
        """
        Lấy định nghĩa metric theo code

        Args:
            code: Mã metric (vd: CIS_62, BBS_100)
            entity_type: Loại entity (COMPANY, BANK, v.v.)
                        Nếu None, tìm trong tất cả entity types

        Returns:
            Dictionary chứa metric definition, hoặc None nếu không tìm thấy

        Ví dụ:
            >>> loader = MetricRegistryLoader()
            >>> metric = loader.get_metric("CIS_62", "COMPANY")
            >>> print(metric['name_vi'])
            'Lợi nhuận sau thuế công ty mẹ'
        """
        # ... existing implementation with Vietnamese comments
```

### Phase 4: Copy Data Registry Files (0.5 ngày)

```bash
# Copy metric_registry.json từ DATA/ sang config/
cd /Users/buuphan/Dev/Vietnam_dashboard

# Backup bản cũ nếu có
if [ -f config/data_registry/metric_registry.json ]; then
    mv config/data_registry/metric_registry.json config/data_registry/metric_registry.json.bak
fi

# Copy bản mới nhất
cp DATA/metadata/metric_registry.json config/data_registry/
cp DATA/metadata/sector_industry_registry.json config/data_registry/

# Verify
ls -lh config/data_registry/
# Kết quả mong đợi:
# -rw-r--r--  metric_registry.json (770K)
# -rw-r--r--  sector_industry_registry.json (~50K)
# -rw-r--r--  ticker_details.json (36K)
```

### Phase 5: Update All Imports (1 ngày)

**Tạo script tự động update imports:**

**File: `scripts/update_imports_after_rename.py`**

```python
#!/usr/bin/env python3
"""
Script tự động update imports sau khi rename config/
====================================================

Tự động tìm và thay thế tất cả imports cũ thành imports mới.

Chạy: python scripts/update_imports_after_rename.py
"""

import re
from pathlib import Path
from typing import List, Tuple

# Mapping: old_import → new_import
IMPORT_MAPPINGS = [
    # SchemaRegistry → SchemaManager
    (
        r'from config\.schema_registry import SchemaRegistry',
        'from config.schema_manager import SchemaManager'
    ),
    (
        r'SchemaRegistry\(\)',
        'SchemaManager()'
    ),

    # MetricRegistry → MetricRegistryLoader
    (
        r'from config\.registries\.metric_lookup import MetricRegistry',
        'from config.registry_classes.metric_registry_loader import MetricRegistryLoader'
    ),
    (
        r'MetricRegistry\(\)',
        'MetricRegistryLoader()'
    ),

    # SectorRegistry → SectorRegistryLoader
    (
        r'from config\.registries\.sector_lookup import SectorRegistry',
        'from config.registry_classes.sector_registry_loader import SectorRegistryLoader'
    ),
    (
        r'SectorRegistry\(\)',
        'SectorRegistryLoader()'
    ),

    # Deprecated imports
    (
        r'from PROCESSORS\.core\.registries\.metric_lookup import MetricRegistry',
        'from config.registry_classes.metric_registry_loader import MetricRegistryLoader'
    ),

    # Schema paths
    (
        r'config/schema_registry/',
        'config/schemas/'
    ),
    (
        r'config/metadata/',
        'config/data_registry/'
    ),
    (
        r'DATA/metadata/metric_registry\.json',
        'config/data_registry/metric_registry.json'
    ),
]


def update_file(file_path: Path) -> Tuple[bool, int]:
    """
    Update imports trong một file

    Returns:
        (đã_thay_đổi, số_dòng_thay_đổi)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Lỗi đọc {file_path}: {e}")
        return False, 0

    original_content = content
    changes_count = 0

    # Apply tất cả replacements
    for old_pattern, new_pattern in IMPORT_MAPPINGS:
        matches = re.findall(old_pattern, content)
        if matches:
            content = re.sub(old_pattern, new_pattern, content)
            changes_count += len(matches)

    # Write back nếu có thay đổi
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes_count

    return False, 0


def main():
    """Tìm và update tất cả Python files"""
    project_root = Path(__file__).parent.parent

    # Các thư mục cần scan
    dirs_to_scan = [
        project_root / "PROCESSORS",
        project_root / "WEBAPP",
        project_root / "config",
    ]

    total_files = 0
    updated_files = 0
    total_changes = 0

    print("=" * 70)
    print("UPDATE IMPORTS AFTER CONFIG RENAME")
    print("=" * 70)

    for dir_path in dirs_to_scan:
        if not dir_path.exists():
            continue

        print(f"\n📁 Scanning {dir_path.relative_to(project_root)}/")

        for py_file in dir_path.rglob("*.py"):
            total_files += 1
            changed, count = update_file(py_file)

            if changed:
                updated_files += 1
                total_changes += count
                print(f"  ✅ {py_file.relative_to(project_root)} - {count} thay đổi")

    print("\n" + "=" * 70)
    print(f"KẾT QUẢ:")
    print(f"  Tổng files scan: {total_files}")
    print(f"  Files đã update: {updated_files}")
    print(f"  Tổng thay đổi: {total_changes}")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

**Chạy script:**
```bash
python scripts/update_imports_after_rename.py
```

### Phase 6: Update Documentation (0.5 ngày)

**Tạo file README mới:**

**File: `config/README_CONFIG_STRUCTURE.md`**

```markdown
# CONFIG SYSTEM STRUCTURE - CẤU TRÚC HỆ THỐNG CONFIG

**Cập nhật:** 2025-12-11
**Version:** 2.0.0 (sau restructure)

---

## 📁 TỔNG QUAN CẤU TRÚC

```
config/
├── registry_classes/           # Python classes để load & lookup data
├── schema_manager.py          # Singleton class quản lý schemas
├── schemas/                   # JSON schema definitions (organized)
├── data_registry/            # PRIMARY SOURCE cho metric & sector data
├── business_rules/           # Business logic configs
├── sector_analysis_config/   # FA/TA sector analysis configs
└── legacy_schemas/           # Legacy schemas (backward compat)
```

---

## 📚 CHI TIẾT TỪNG COMPONENT

### 1. Registry Classes (`registry_classes/`)

**Python classes để load và lookup data từ JSON registries.**

| File | Class | Mục đích |
|------|-------|----------|
| `metric_registry_loader.py` | `MetricRegistryLoader` | Load & lookup 2,099 metrics |
| `sector_registry_loader.py` | `SectorRegistryLoader` | Load & lookup 457 tickers × 19 sectors |
| `builders/build_metric_registry.py` | Script | Build metric_registry.json từ BSC Excel |
| `builders/build_sector_registry.py` | Script | Build sector_registry.json từ metadata |

**Import pattern:**
```python
from config.registry_classes.metric_registry_loader import MetricRegistryLoader
from config.registry_classes.sector_registry_loader import SectorRegistryLoader

metric_loader = MetricRegistryLoader()
sector_loader = SectorRegistryLoader()
```

### 2. Schema Manager (`schema_manager.py`)

**Singleton class quản lý tất cả schemas.**

**Chức năng:**
- Load schemas từ `config/schemas/`
- Format data (price, volume, percentage, v.v.)
- Get colors từ theme
- Validate data

**Import pattern:**
```python
from config.schema_manager import SchemaManager

schema_mgr = SchemaManager()
price = schema_mgr.format_price(25750.5)  # "25,750.50đ"
```

### 3. Schemas (`schemas/`)

**Organized JSON schema definitions.**

```
schemas/
├── core/              # Core schemas (types, entities, mappings)
├── domains/           # Domain schemas (fundamental, technical, valuation)
└── display/           # Display schemas (charts, tables, dashboards)
```

**Access pattern:**
```python
schema_mgr = SchemaManager()
metrics = schema_mgr.get_domain_schema('fundamental', 'metrics')
charts = schema_mgr.get_display_schema('charts')
```

### 4. Data Registry (`data_registry/`)

**PRIMARY SOURCE cho tất cả registry data.**

| File | Size | Mô tả |
|------|------|-------|
| `metric_registry.json` | 770 KB | 2,099 financial metrics (Việt ↔ Anh) |
| `sector_industry_registry.json` | ~50 KB | 457 tickers × 19 sectors × 4 entity types |
| `ticker_details.json` | 36 KB | Chi tiết thông tin ticker |

**⚠️ QUAN TRỌNG:**
- **LUÔN LUÔN** import từ `config/data_registry/`
- **KHÔNG BAO GIỜ** truy cập trực tiếp `DATA/metadata/`
- `DATA/metadata/` chỉ dùng làm backup/rebuild source

### 5. Business Rules (`business_rules/`)

**Business logic configurations.**

```
business_rules/
├── analysis_configs/    # FA/TA/Valuation analysis configs
├── decision_rules/      # Trading decision rules, weights, thresholds
└── alert_configs/       # Alert rules, channels, subscriptions
```

### 6. Sector Analysis Config (`sector_analysis_config/`)

**Configs cho FA/TA sector analysis.**

- `fa_ta_weights_manager.py` - Quản lý FA/TA weights và preferences

### 7. Legacy Schemas (`legacy_schemas/`)

**Legacy schemas cho backward compatibility.**

- `master_display_config.json` - Formatting, colors, validation (vẫn sử dụng)
- `archived/` - Old schemas (chuẩn bị xóa)

---

## 🔄 NAMING CHANGES - BẢNG ĐỐI CHIẾU

### Python Files

| Cũ | Mới |
|----|-----|
| `schema_registry.py` | `schema_manager.py` |
| `registries/metric_lookup.py` | `registry_classes/metric_registry_loader.py` |
| `registries/sector_lookup.py` | `registry_classes/sector_registry_loader.py` |

### Folders

| Cũ | Mới |
|----|-----|
| `registries/` | `registry_classes/` |
| `schema_registry/` | `schemas/` |
| `metadata/` | `data_registry/` |
| `business_logic/` | `business_rules/` |
| `schemas/` | `legacy_schemas/` |

---

## ✅ IMPORT CHECKLIST

**Khi viết code mới, luôn sử dụng:**

```python
# ✅ ĐÚNG
from config.schema_manager import SchemaManager
from config.registry_classes.metric_registry_loader import MetricRegistryLoader
from config.registry_classes.sector_registry_loader import SectorRegistryLoader

# ❌ SAI - Deprecated imports
from config.schema_registry import SchemaRegistry
from config.registries.metric_lookup import MetricRegistry
from PROCESSORS.core.registries.metric_lookup import MetricRegistry
```

---

## 🔧 REBUILD REGISTRIES

### Rebuild Metric Registry

```bash
python config/registry_classes/builders/build_metric_registry.py
# Output: config/data_registry/metric_registry.json
```

### Rebuild Sector Registry

```bash
python config/registry_classes/builders/build_sector_registry.py
# Output: config/data_registry/sector_industry_registry.json
```

---

## 📝 DOCSTRINGS GUIDELINES

**Tất cả code mới phải có docstrings tiếng Việt:**

```python
def format_price(self, value: float) -> str:
    """
    Format giá tiền theo quy tắc hiển thị

    Args:
        value: Giá trị cần format (VND)

    Returns:
        Chuỗi đã format (vd: "25,750.50đ")

    Ví dụ:
        >>> format_price(25750.5)
        '25,750.50đ'
    """
    # Implementation...
```
```

---

## 6. TESTING & VALIDATION

### Test 1: Verify Imports Work

```python
#!/usr/bin/env python3
"""Test imports sau khi rename"""

# Test SchemaManager
try:
    from config.schema_manager import SchemaManager
    sm = SchemaManager()
    print("✅ SchemaManager import thành công")
except Exception as e:
    print(f"❌ SchemaManager lỗi: {e}")

# Test MetricRegistryLoader
try:
    from config.registry_classes.metric_registry_loader import MetricRegistryLoader
    mrl = MetricRegistryLoader()
    print("✅ MetricRegistryLoader import thành công")
except Exception as e:
    print(f"❌ MetricRegistryLoader lỗi: {e}")

# Test SectorRegistryLoader
try:
    from config.registry_classes.sector_registry_loader import SectorRegistryLoader
    srl = SectorRegistryLoader()
    print("✅ SectorRegistryLoader import thành công")
except Exception as e:
    print(f"❌ SectorRegistryLoader lỗi: {e}")
```

### Test 2: Verify Data Registry Access

```python
#!/usr/bin/env python3
"""Test data registry paths"""

from pathlib import Path

project_root = Path("/Users/buuphan/Dev/Vietnam_dashboard")

# Check files exist
files_to_check = [
    "config/data_registry/metric_registry.json",
    "config/data_registry/sector_industry_registry.json",
    "config/data_registry/ticker_details.json",
]

for file_path in files_to_check:
    full_path = project_root / file_path
    if full_path.exists():
        size = full_path.stat().st_size / 1024  # KB
        print(f"✅ {file_path} ({size:.1f} KB)")
    else:
        print(f"❌ {file_path} KHÔNG TỒN TẠI")
```

---

## 7. ROLLBACK PLAN

**Nếu gặp vấn đề, rollback:**

```bash
# Restore từ backup
cd /Users/buuphan/Dev/Vietnam_dashboard
rm -rf config/
cp -r config_backup_2025_12_11/ config/

# Verify
ls -la config/
```

---

## 8. SUCCESS CRITERIA

### ✅ Checklist hoàn thành

- [ ] Tất cả folders đã rename
- [ ] Tất cả Python files đã rename
- [ ] Tất cả imports đã update
- [ ] Data registry files đã copy
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No confusing naming conflicts
- [ ] All docstrings in Vietnamese

---

## 9. TIMELINE

| Phase | Task | Thời gian | Status |
|-------|------|-----------|--------|
| 0 | Backup & preparation | 0.5 ngày | ⏳ Pending |
| 1 | Rename folders | 0.5 ngày | ⏳ Pending |
| 2 | Rename Python files | 0.5 ngày | ⏳ Pending |
| 3 | Update class names & docstrings | 1 ngày | ⏳ Pending |
| 4 | Copy data registry files | 0.5 ngày | ⏳ Pending |
| 5 | Update all imports | 1 ngày | ⏳ Pending |
| 6 | Update documentation | 0.5 ngày | ⏳ Pending |
| **TOTAL** | **4.5 ngày** | **~1 tuần** | |

---

## CONCLUSION

Restructure này giải quyết toàn bộ naming conflicts, tạo ra cấu trúc rõ ràng và dễ maintain. Mọi file/folder có tên mô tả chính xác chức năng, không còn trùng lặp gây nhầm lẫn.

**Lợi ích:**
1. ✅ Không còn confusion giữa file vs folder
2. ✅ Single source of truth rõ ràng (`config/data_registry/`)
3. ✅ Tên files/classes descriptive hơn
4. ✅ Docstrings tiếng Việt dễ đọc
5. ✅ Dễ maintain và scale

---

**Plan Status:** READY FOR REVIEW & APPROVAL
**Next Steps:** Review → Approve → Backup → Execute Phase by Phase
