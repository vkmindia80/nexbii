# Visual Query Configuration Save/Load Feature

## Overview
This document describes the implementation of the ability to **save and load visual query configurations** in the NexBII Business Intelligence platform.

## Feature Description
Users can now create queries using the Visual Query Builder, save them with their complete configuration, and later edit them with the visual builder state fully restored.

## Implementation Date
October 23, 2025

---

## Technical Implementation

### Backend Changes
**Status:** ✅ **No changes needed** - Already supported!

The backend was already prepared to handle visual query configurations:

#### Database Model (`/app/backend/app/models/query.py`)
```python
class Query(Base):
    query_type = Column(String)  # 'visual' or 'sql'
    query_config = Column(JSON)  # Visual query builder config
    sql_query = Column(Text)     # Generated SQL
```

#### API Schema (`/app/backend/app/schemas/query.py`)
```python
class QueryBase(BaseModel):
    query_type: str  # 'visual' or 'sql'
    query_config: Optional[Dict[str, Any]] = None
    sql_query: Optional[str] = None
```

#### API Endpoints (`/app/backend/app/api/v1/queries.py`)
- ✅ `POST /api/queries/` - Creates query with query_type and query_config
- ✅ `PUT /api/queries/{id}` - Updates query with query_type and query_config
- ✅ `GET /api/queries/` - Returns queries with their configurations

---

### Frontend Changes

#### 1. VisualQueryBuilder Component (`/app/frontend/src/components/VisualQueryBuilder.tsx`)

**New Exported Interface:**
```typescript
export interface VisualQueryConfig {
  selectedTable: string;
  selectedColumns: SelectedColumn[];
  filters: FilterCondition[];
  joins: JoinCondition[];
  groupBy: GroupByColumn[];
  orderBy: OrderByColumn[];
  limit: number;
  distinct: boolean;
}
```

**New Props:**
```typescript
interface VisualQueryBuilderProps {
  schema: { tables: TableSchema[] } | null;
  onQueryGenerated: (sql: string) => void;
  darkMode?: boolean;
  initialConfig?: VisualQueryConfig | null;      // NEW: Load saved config
  onConfigChange?: (config: VisualQueryConfig) => void;  // NEW: Track changes
}
```

**Key Features Added:**
- **State Import:** Loads initial configuration when provided
- **State Export:** Notifies parent component of all configuration changes
- **Initialization Guard:** Uses `isInitialized` flag to prevent re-initialization
- **Reset Function:** Properly resets initialization state

**Implementation Details:**
```typescript
// Load initial configuration on mount
useEffect(() => {
  if (initialConfig && !isInitialized && schema) {
    setSelectedTable(initialConfig.selectedTable || '');
    setSelectedColumns(initialConfig.selectedColumns || []);
    setFilters(initialConfig.filters || []);
    setJoins(initialConfig.joins || []);
    setGroupBy(initialConfig.groupBy || []);
    setOrderBy(initialConfig.orderBy || []);
    setLimit(initialConfig.limit || 100);
    setDistinct(initialConfig.distinct || false);
    setIsInitialized(true);
  }
}, [initialConfig, schema, isInitialized]);

// Export configuration changes
useEffect(() => {
  const sql = generateSQL();
  setGeneratedSQL(sql);
  onQueryGenerated(sql);
  
  if (onConfigChange) {
    const config: VisualQueryConfig = {
      selectedTable,
      selectedColumns,
      filters,
      joins,
      groupBy,
      orderBy,
      limit,
      distinct
    };
    onConfigChange(config);
  }
}, [selectedTable, selectedColumns, filters, joins, groupBy, orderBy, limit, distinct]);
```

---

#### 2. QueriesPage Component (`/app/frontend/src/pages/QueriesPage.tsx`)

**New State Variable:**
```typescript
const [visualConfig, setVisualConfig] = useState<VisualQueryConfig | null>(null);
```

**Enhanced handleSubmit Function:**
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  try {
    const queryData: any = {
      name: formData.name,
      description: formData.description,
      datasource_id: formData.datasource_id,
      query_type: queryMode,  // 'visual' or 'sql'
      sql_query: formData.sql_query
    };

    // Include visual config if in visual mode
    if (queryMode === 'visual' && visualConfig) {
      queryData.query_config = visualConfig;
    }

    if (editingQuery) {
      await queryService.update(editingQuery.id, queryData);
    } else {
      await queryService.create(queryData);
    }
    
    // Reset states
    setVisualConfig(null);
    setQueryMode('sql');
    // ... other resets
  } catch (error) {
    console.error('Failed to save query:', error);
  }
};
```

**Enhanced handleEdit Function:**
```typescript
const handleEdit = async (query: Query) => {
  setEditingQuery(query);
  setFormData({
    name: query.name,
    description: query.description || '',
    datasource_id: query.datasource_id,
    sql_query: query.sql_query || 'SELECT * FROM customers LIMIT 10;'
  });
  
  // Set query mode and load visual config if it exists
  if (query.query_type === 'visual' && query.query_config) {
    setQueryMode('visual');
    setVisualConfig(query.query_config);
  } else {
    setQueryMode('sql');
    setVisualConfig(null);
  }
  
  setShowModal(true);
  if (query.datasource_id) {
    await loadSchema(query.datasource_id);
  }
};
```

**Updated VisualQueryBuilder Integration:**
```typescript
{queryMode === 'visual' && (
  <div className="max-h-[500px] overflow-y-auto">
    <VisualQueryBuilder
      schema={schemaCache}
      onQueryGenerated={(sql) => setFormData({ ...formData, sql_query: sql })}
      darkMode={darkMode}
      initialConfig={visualConfig}           // Pass saved config
      onConfigChange={(config) => setVisualConfig(config)}  // Track changes
    />
  </div>
)}
```

**Enhanced Query List UI:**
```typescript
// Visual indicator for query type
<div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
  query.query_type === 'visual' ? 'bg-purple-100' : 'bg-green-100'
}`}>
  {query.query_type === 'visual' ? (
    <BarChart3 className="w-5 h-5 text-purple-600" />
  ) : (
    <FileText className="w-5 h-5 text-green-600" />
  )}
</div>

// Badge showing query type
<span className={`text-xs px-2 py-0.5 rounded-full ${
  query.query_type === 'visual' 
    ? 'bg-purple-100 text-purple-700' 
    : 'bg-green-100 text-green-700'
}`}>
  {query.query_type === 'visual' ? 'Visual Builder' : 'SQL'}
</span>
```

**New Query Button Reset:**
```typescript
onClick={() => {
  setEditingQuery(null);
  setQueryMode('sql');
  setVisualConfig(null);  // Reset visual config
  // ... other resets
}}
```

---

## Bug Fixes

### TypeScript Import Error
**Issue:** `Columns3` icon doesn't exist in lucide-react  
**Fix:** Changed to `Columns` icon

```typescript
// Before
import { ..., Columns3, ... } from 'lucide-react';

// After
import { ..., Columns, ... } from 'lucide-react';
```

---

## How It Works

### Creating a Visual Query

1. User clicks "New Query" button
2. Switches to "Visual" mode using the mode toggle
3. Builds query using visual interface:
   - Selects table
   - Adds columns with aggregations
   - Adds filters (WHERE conditions)
   - Adds joins
   - Adds GROUP BY and ORDER BY clauses
   - Sets LIMIT and DISTINCT
4. SQL is generated in real-time
5. User enters query name and description
6. Clicks "Save Query"
7. **Backend saves:**
   - `query_type: 'visual'`
   - `query_config: { selectedTable, selectedColumns, filters, ... }`
   - `sql_query: 'SELECT ...'`

### Editing a Visual Query

1. User clicks "Edit" on a visual query
2. Modal opens with mode automatically set to "Visual"
3. **VisualQueryBuilder loads saved configuration:**
   - Restores selected table
   - Restores selected columns with aggregations
   - Restores filters with operators and values
   - Restores joins
   - Restores GROUP BY and ORDER BY
   - Restores LIMIT and DISTINCT settings
4. User can modify the query visually
5. Changes are tracked in real-time
6. User clicks "Save" to update
7. Backend updates with new configuration

### Editing an SQL Query

1. User clicks "Edit" on an SQL query
2. Modal opens with mode set to "SQL"
3. Monaco editor shows the SQL query
4. User can edit SQL directly
5. Or switch to Visual mode (starts fresh)

---

## Visual Query Configuration Structure

```json
{
  "selectedTable": "orders",
  "selectedColumns": [
    {
      "id": "1698765432123",
      "table": "orders",
      "column": "order_date",
      "alias": "Date",
      "aggregation": ""
    },
    {
      "id": "1698765432124",
      "table": "orders",
      "column": "total_amount",
      "alias": "Revenue",
      "aggregation": "SUM"
    }
  ],
  "filters": [
    {
      "id": "1698765432125",
      "column": "orders.status",
      "operator": "=",
      "value": "completed"
    }
  ],
  "joins": [
    {
      "id": "1698765432126",
      "type": "INNER JOIN",
      "leftTable": "orders",
      "rightTable": "customers",
      "leftColumn": "customer_id",
      "rightColumn": "id"
    }
  ],
  "groupBy": [
    {
      "id": "1698765432127",
      "column": "orders.order_date"
    }
  ],
  "orderBy": [
    {
      "id": "1698765432128",
      "column": "orders.order_date",
      "direction": "DESC"
    }
  ],
  "limit": 100,
  "distinct": false
}
```

---

## Testing

### Manual Testing Checklist

- [x] Backend services running
- [x] Frontend compiled successfully
- [ ] Create a new visual query
- [ ] Save the visual query
- [ ] Edit the visual query (config should be loaded)
- [ ] Modify and re-save the visual query
- [ ] Create an SQL query
- [ ] Edit SQL query (should stay in SQL mode)
- [ ] Switch between SQL and Visual modes
- [ ] Verify query list shows correct badges

### Test Scenarios

**Scenario 1: Create and Edit Visual Query**
1. Create new query in Visual mode
2. Select table "customers"
3. Add columns: name, email, created_at
4. Add filter: status = 'active'
5. Add ORDER BY: created_at DESC
6. Save as "Active Customers"
7. Close modal
8. Edit "Active Customers"
9. Verify: Visual mode is active, all settings restored
10. Add filter: country = 'USA'
11. Save
12. Verify: Query updated successfully

**Scenario 2: SQL Query Remains SQL**
1. Create new query in SQL mode
2. Write custom SQL
3. Save as "Custom Report"
4. Edit "Custom Report"
5. Verify: SQL mode is active, Monaco editor shows SQL
6. Modify SQL
7. Save
8. Verify: Changes saved as SQL query

---

## Benefits

### For Users
- ✅ **No Re-building:** Save complex visual queries and edit them later
- ✅ **Version Control:** Modify queries without starting from scratch
- ✅ **Mode Flexibility:** Create in visual mode, switch to SQL if needed
- ✅ **Visual Clarity:** See query type at a glance with badges and icons

### For Developers
- ✅ **Clean Architecture:** Configuration stored as JSON in database
- ✅ **Type Safety:** Full TypeScript interfaces for configuration
- ✅ **Maintainability:** Configuration structure is well-documented
- ✅ **Extensibility:** Easy to add new visual query features

---

## Files Modified

### Frontend
1. `/app/frontend/src/components/VisualQueryBuilder.tsx`
   - Added `VisualQueryConfig` interface (exported)
   - Added `initialConfig` and `onConfigChange` props
   - Implemented state import/export logic
   - Fixed icon import (Columns3 → Columns)

2. `/app/frontend/src/pages/QueriesPage.tsx`
   - Added `visualConfig` state
   - Updated `handleSubmit` to save configurations
   - Updated `handleEdit` to load configurations
   - Enhanced query list UI with type badges
   - Updated VisualQueryBuilder integration

### Backend
- **No changes required** (already supported)

---

## Known Limitations

1. **Mode Switching:** Switching from Visual to SQL mode in the same session will lose visual state (expected behavior)
2. **SQL to Visual:** Cannot convert arbitrary SQL queries back to visual configuration
3. **Complex SQL:** Some advanced SQL features may not be representable in visual mode

---

## Future Enhancements

1. **SQL Parser:** Automatically detect and convert simple SQL to visual config
2. **Templates:** Save visual query configurations as reusable templates
3. **Query Validation:** Warn users before switching modes if they have unsaved changes
4. **Import/Export:** Allow exporting visual configurations as JSON files
5. **Diff View:** Show changes when editing visual queries

---

## Conclusion

The Visual Query Configuration Save/Load feature is now **fully implemented** and ready for testing. Users can create complex queries using the visual builder, save them with their complete configuration, and later edit them with all settings restored.

This feature significantly improves the user experience by eliminating the need to rebuild queries from scratch when making modifications.

---

**Implementation Status:** ✅ **COMPLETE**  
**Ready for Testing:** ✅ **YES**  
**Breaking Changes:** ❌ **NO**  
**Database Migration Required:** ❌ **NO** (already supported)
