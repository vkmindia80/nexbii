import React, { useState, useEffect } from 'react';
import { Plus, X, Trash2, Copy, ChevronDown, Database, Table2, Columns3, Filter, Link, BarChart3 } from 'lucide-react';

interface Column {
  column_name: string;
  data_type: string;
}

interface TableSchema {
  table_name: string;
  columns: Column[];
}

interface SelectedColumn {
  id: string;
  table: string;
  column: string;
  alias?: string;
  aggregation?: string;
}

interface FilterCondition {
  id: string;
  column: string;
  operator: string;
  value: string;
}

interface JoinCondition {
  id: string;
  type: string;
  leftTable: string;
  rightTable: string;
  leftColumn: string;
  rightColumn: string;
}

interface GroupByColumn {
  id: string;
  column: string;
}

interface OrderByColumn {
  id: string;
  column: string;
  direction: 'ASC' | 'DESC';
}

interface VisualQueryBuilderProps {
  schema: { tables: TableSchema[] } | null;
  onQueryGenerated: (sql: string) => void;
  darkMode?: boolean;
}

const OPERATORS = [
  { value: '=', label: 'Equals (=)' },
  { value: '!=', label: 'Not Equals (!=)' },
  { value: '>', label: 'Greater Than (>)' },
  { value: '<', label: 'Less Than (<)' },
  { value: '>=', label: 'Greater or Equal (>=)' },
  { value: '<=', label: 'Less or Equal (<=)' },
  { value: 'LIKE', label: 'Contains (LIKE)' },
  { value: 'NOT LIKE', label: 'Not Contains (NOT LIKE)' },
  { value: 'IN', label: 'In List (IN)' },
  { value: 'NOT IN', label: 'Not In List (NOT IN)' },
  { value: 'IS NULL', label: 'Is Null' },
  { value: 'IS NOT NULL', label: 'Is Not Null' },
  { value: 'BETWEEN', label: 'Between' },
];

const AGGREGATIONS = [
  { value: '', label: 'None' },
  { value: 'COUNT', label: 'COUNT' },
  { value: 'SUM', label: 'SUM' },
  { value: 'AVG', label: 'AVG' },
  { value: 'MIN', label: 'MIN' },
  { value: 'MAX', label: 'MAX' },
  { value: 'COUNT(DISTINCT', label: 'COUNT DISTINCT' },
];

const JOIN_TYPES = [
  { value: 'INNER JOIN', label: 'Inner Join' },
  { value: 'LEFT JOIN', label: 'Left Join' },
  { value: 'RIGHT JOIN', label: 'Right Join' },
  { value: 'FULL JOIN', label: 'Full Join' },
];

const VisualQueryBuilder: React.FC<VisualQueryBuilderProps> = ({
  schema,
  onQueryGenerated,
  darkMode = false
}) => {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [selectedColumns, setSelectedColumns] = useState<SelectedColumn[]>([]);
  const [filters, setFilters] = useState<FilterCondition[]>([]);
  const [joins, setJoins] = useState<JoinCondition[]>([]);
  const [groupBy, setGroupBy] = useState<GroupByColumn[]>([]);
  const [orderBy, setOrderBy] = useState<OrderByColumn[]>([]);
  const [limit, setLimit] = useState<number>(100);
  const [distinct, setDistinct] = useState<boolean>(false);
  const [generatedSQL, setGeneratedSQL] = useState<string>('');

  // Generate SQL whenever any state changes
  useEffect(() => {
    const sql = generateSQL();
    setGeneratedSQL(sql);
    onQueryGenerated(sql);
  }, [selectedTable, selectedColumns, filters, joins, groupBy, orderBy, limit, distinct]);

  const generateSQL = (): string => {
    if (!selectedTable) return '';

    let sql = 'SELECT ';
    
    // DISTINCT
    if (distinct) {
      sql += 'DISTINCT ';
    }

    // Columns
    if (selectedColumns.length === 0) {
      sql += '*';
    } else {
      sql += selectedColumns.map(col => {
        let colStr = `${col.table}.${col.column}`;
        if (col.aggregation) {
          if (col.aggregation === 'COUNT(DISTINCT') {
            colStr = `${col.aggregation} ${col.table}.${col.column})`;
          } else {
            colStr = `${col.aggregation}(${col.table}.${col.column})`;
          }
        }
        if (col.alias) {
          colStr += ` AS ${col.alias}`;
        }
        return colStr;
      }).join(', ');
    }

    // FROM
    sql += `\nFROM ${selectedTable}`;

    // JOINs
    if (joins.length > 0) {
      joins.forEach(join => {
        sql += `\n${join.type} ${join.rightTable} ON ${join.leftTable}.${join.leftColumn} = ${join.rightTable}.${join.rightColumn}`;
      });
    }

    // WHERE
    if (filters.length > 0) {
      sql += '\nWHERE ';
      sql += filters.map(filter => {
        if (filter.operator === 'IS NULL' || filter.operator === 'IS NOT NULL') {
          return `${filter.column} ${filter.operator}`;
        } else if (filter.operator === 'LIKE' || filter.operator === 'NOT LIKE') {
          return `${filter.column} ${filter.operator} '%${filter.value}%'`;
        } else if (filter.operator === 'IN' || filter.operator === 'NOT IN') {
          return `${filter.column} ${filter.operator} (${filter.value})`;
        } else if (filter.operator === 'BETWEEN') {
          const values = filter.value.split(',');
          return `${filter.column} BETWEEN ${values[0]} AND ${values[1]}`;
        } else {
          // Check if value is numeric
          const isNumeric = !isNaN(Number(filter.value));
          const quotedValue = isNumeric ? filter.value : `'${filter.value}'`;
          return `${filter.column} ${filter.operator} ${quotedValue}`;
        }
      }).join(' AND ');
    }

    // GROUP BY
    if (groupBy.length > 0) {
      sql += '\nGROUP BY ' + groupBy.map(g => g.column).join(', ');
    }

    // ORDER BY
    if (orderBy.length > 0) {
      sql += '\nORDER BY ' + orderBy.map(o => `${o.column} ${o.direction}`).join(', ');
    }

    // LIMIT
    sql += `\nLIMIT ${limit};`;

    return sql;
  };

  const addColumn = () => {
    if (!selectedTable || !schema) return;
    const table = schema.tables.find(t => t.table_name === selectedTable);
    if (!table || table.columns.length === 0) return;

    const newColumn: SelectedColumn = {
      id: Date.now().toString(),
      table: selectedTable,
      column: table.columns[0].column_name,
      alias: '',
      aggregation: ''
    };
    setSelectedColumns([...selectedColumns, newColumn]);
  };

  const updateColumn = (id: string, field: keyof SelectedColumn, value: string) => {
    setSelectedColumns(selectedColumns.map(col =>
      col.id === id ? { ...col, [field]: value } : col
    ));
  };

  const removeColumn = (id: string) => {
    setSelectedColumns(selectedColumns.filter(col => col.id !== id));
  };

  const addFilter = () => {
    if (!selectedTable) return;
    const newFilter: FilterCondition = {
      id: Date.now().toString(),
      column: `${selectedTable}.*`,
      operator: '=',
      value: ''
    };
    setFilters([...filters, newFilter]);
  };

  const updateFilter = (id: string, field: keyof FilterCondition, value: string) => {
    setFilters(filters.map(f =>
      f.id === id ? { ...f, [field]: value } : f
    ));
  };

  const removeFilter = (id: string) => {
    setFilters(filters.filter(f => f.id !== id));
  };

  const addJoin = () => {
    if (!selectedTable || !schema || schema.tables.length < 2) return;
    const otherTable = schema.tables.find(t => t.table_name !== selectedTable);
    if (!otherTable) return;

    const newJoin: JoinCondition = {
      id: Date.now().toString(),
      type: 'INNER JOIN',
      leftTable: selectedTable,
      rightTable: otherTable.table_name,
      leftColumn: schema.tables.find(t => t.table_name === selectedTable)?.columns[0]?.column_name || 'id',
      rightColumn: otherTable.columns[0]?.column_name || 'id'
    };
    setJoins([...joins, newJoin]);
  };

  const updateJoin = (id: string, field: keyof JoinCondition, value: string) => {
    setJoins(joins.map(j =>
      j.id === id ? { ...j, [field]: value } : j
    ));
  };

  const removeJoin = (id: string) => {
    setJoins(joins.filter(j => j.id !== id));
  };

  const addGroupBy = () => {
    if (!selectedTable) return;
    const newGroupBy: GroupByColumn = {
      id: Date.now().toString(),
      column: `${selectedTable}.*`
    };
    setGroupBy([...groupBy, newGroupBy]);
  };

  const updateGroupBy = (id: string, value: string) => {
    setGroupBy(groupBy.map(g =>
      g.id === id ? { ...g, column: value } : g
    ));
  };

  const removeGroupBy = (id: string) => {
    setGroupBy(groupBy.filter(g => g.id !== id));
  };

  const addOrderBy = () => {
    if (!selectedTable) return;
    const newOrderBy: OrderByColumn = {
      id: Date.now().toString(),
      column: `${selectedTable}.*`,
      direction: 'ASC'
    };
    setOrderBy([...orderBy, newOrderBy]);
  };

  const updateOrderBy = (id: string, field: 'column' | 'direction', value: string) => {
    setOrderBy(orderBy.map(o =>
      o.id === id ? { ...o, [field]: value } : o
    ));
  };

  const removeOrderBy = (id: string) => {
    setOrderBy(orderBy.filter(o => o.id !== id));
  };

  const getAllColumns = (): string[] => {
    if (!schema) return [];
    const columns: string[] = [];
    
    // Add columns from selected table
    const table = schema.tables.find(t => t.table_name === selectedTable);
    if (table) {
      table.columns.forEach(col => {
        columns.push(`${table.table_name}.${col.column_name}`);
      });
    }

    // Add columns from joined tables
    joins.forEach(join => {
      const joinedTable = schema.tables.find(t => t.table_name === join.rightTable);
      if (joinedTable) {
        joinedTable.columns.forEach(col => {
          columns.push(`${joinedTable.table_name}.${col.column_name}`);
        });
      }
    });

    return columns;
  };

  const resetBuilder = () => {
    setSelectedTable('');
    setSelectedColumns([]);
    setFilters([]);
    setJoins([]);
    setGroupBy([]);
    setOrderBy([]);
    setLimit(100);
    setDistinct(false);
  };

  if (!schema || schema.tables.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
        <p className="text-yellow-800 font-medium">No schema available</p>
        <p className="text-sm text-yellow-600 mt-1">Please select a data source with schema information</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center">
          <BarChart3 className="w-5 h-5 mr-2" />
          Visual Query Builder
        </h3>
        <button
          onClick={resetBuilder}
          className="text-sm text-red-600 hover:text-red-700 flex items-center space-x-1"
        >
          <Trash2 className="w-4 h-4" />
          <span>Reset</span>
        </button>
      </div>

      {/* Select Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <label className="block text-sm font-medium mb-2 flex items-center">
          <Database className="w-4 h-4 mr-2" />
          Select Table
        </label>
        <select
          value={selectedTable}
          onChange={(e) => {
            setSelectedTable(e.target.value);
            setSelectedColumns([]);
            setFilters([]);
            setJoins([]);
            setGroupBy([]);
            setOrderBy([]);
          }}
          className="input w-full"
          data-testid="select-table"
        >
          <option value="">-- Choose a table --</option>
          {schema.tables.map(table => (
            <option key={table.table_name} value={table.table_name}>
              {table.table_name}
            </option>
          ))}
        </select>
      </div>

      {selectedTable && (
        <>
          {/* Select Columns */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium flex items-center">
                <Columns3 className="w-4 h-4 mr-2" />
                Select Columns {selectedColumns.length === 0 && <span className="text-gray-500 ml-2">(* all columns)</span>}
              </label>
              <button
                onClick={addColumn}
                className="text-sm bg-primary-600 text-white px-3 py-1 rounded hover:bg-primary-700 flex items-center space-x-1"
                data-testid="add-column"
              >
                <Plus className="w-4 h-4" />
                <span>Add Column</span>
              </button>
            </div>

            <div className="flex items-center space-x-2 mb-3">
              <input
                type="checkbox"
                id="distinct"
                checked={distinct}
                onChange={(e) => setDistinct(e.target.checked)}
                className="rounded border-gray-300"
              />
              <label htmlFor="distinct" className="text-sm">DISTINCT (unique rows only)</label>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {selectedColumns.map(col => {
                const table = schema.tables.find(t => t.table_name === col.table);
                return (
                  <div key={col.id} className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                    <select
                      value={col.table}
                      onChange={(e) => updateColumn(col.id, 'table', e.target.value)}
                      className="input flex-1"
                    >
                      <option value={selectedTable}>{selectedTable}</option>
                      {joins.map(j => (
                        <option key={j.id} value={j.rightTable}>{j.rightTable}</option>
                      ))}
                    </select>
                    <select
                      value={col.column}
                      onChange={(e) => updateColumn(col.id, 'column', e.target.value)}
                      className="input flex-1"
                    >
                      {table?.columns.map(c => (
                        <option key={c.column_name} value={c.column_name}>
                          {c.column_name} ({c.data_type})
                        </option>
                      ))}
                    </select>
                    <select
                      value={col.aggregation}
                      onChange={(e) => updateColumn(col.id, 'aggregation', e.target.value)}
                      className="input w-32"
                      title="Aggregation"
                    >
                      {AGGREGATIONS.map(agg => (
                        <option key={agg.value} value={agg.value}>{agg.label}</option>
                      ))}
                    </select>
                    <input
                      type="text"
                      value={col.alias}
                      onChange={(e) => updateColumn(col.id, 'alias', e.target.value)}
                      placeholder="Alias"
                      className="input w-24"
                    />
                    <button
                      onClick={() => removeColumn(col.id)}
                      className="text-red-600 hover:text-red-700 p-1"
                      title="Remove column"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Joins */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium flex items-center">
                <Link className="w-4 h-4 mr-2" />
                Joins
              </label>
              <button
                onClick={addJoin}
                className="text-sm bg-primary-600 text-white px-3 py-1 rounded hover:bg-primary-700 flex items-center space-x-1"
                data-testid="add-join"
              >
                <Plus className="w-4 h-4" />
                <span>Add Join</span>
              </button>
            </div>

            <div className="space-y-2">
              {joins.map(join => (
                <div key={join.id} className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                  <select
                    value={join.type}
                    onChange={(e) => updateJoin(join.id, 'type', e.target.value)}
                    className="input w-32"
                  >
                    {JOIN_TYPES.map(jt => (
                      <option key={jt.value} value={jt.value}>{jt.label}</option>
                    ))}
                  </select>
                  <select
                    value={join.rightTable}
                    onChange={(e) => updateJoin(join.id, 'rightTable', e.target.value)}
                    className="input flex-1"
                  >
                    {schema.tables.filter(t => t.table_name !== selectedTable).map(t => (
                      <option key={t.table_name} value={t.table_name}>{t.table_name}</option>
                    ))}
                  </select>
                  <span className="text-sm">ON</span>
                  <select
                    value={`${join.leftTable}.${join.leftColumn}`}
                    onChange={(e) => {
                      const [table, col] = e.target.value.split('.');
                      updateJoin(join.id, 'leftColumn', col);
                    }}
                    className="input flex-1"
                  >
                    {schema.tables.find(t => t.table_name === join.leftTable)?.columns.map(c => (
                      <option key={c.column_name} value={`${join.leftTable}.${c.column_name}`}>
                        {join.leftTable}.{c.column_name}
                      </option>
                    ))}
                  </select>
                  <span className="text-sm">=</span>
                  <select
                    value={`${join.rightTable}.${join.rightColumn}`}
                    onChange={(e) => {
                      const [table, col] = e.target.value.split('.');
                      updateJoin(join.id, 'rightColumn', col);
                    }}
                    className="input flex-1"
                  >
                    {schema.tables.find(t => t.table_name === join.rightTable)?.columns.map(c => (
                      <option key={c.column_name} value={`${join.rightTable}.${c.column_name}`}>
                        {join.rightTable}.{c.column_name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => removeJoin(join.id)}
                    className="text-red-600 hover:text-red-700 p-1"
                    title="Remove join"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Filters (WHERE) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-medium flex items-center">
                <Filter className="w-4 h-4 mr-2" />
                Filters (WHERE)
              </label>
              <button
                onClick={addFilter}
                className="text-sm bg-primary-600 text-white px-3 py-1 rounded hover:bg-primary-700 flex items-center space-x-1"
                data-testid="add-filter"
              >
                <Plus className="w-4 h-4" />
                <span>Add Filter</span>
              </button>
            </div>

            <div className="space-y-2">
              {filters.map(filter => (
                <div key={filter.id} className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-700 p-2 rounded">
                  <select
                    value={filter.column}
                    onChange={(e) => updateFilter(filter.id, 'column', e.target.value)}
                    className="input flex-1"
                  >
                    {getAllColumns().map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                  <select
                    value={filter.operator}
                    onChange={(e) => updateFilter(filter.id, 'operator', e.target.value)}
                    className="input w-40"
                  >
                    {OPERATORS.map(op => (
                      <option key={op.value} value={op.value}>{op.label}</option>
                    ))}
                  </select>
                  {!['IS NULL', 'IS NOT NULL'].includes(filter.operator) && (
                    <input
                      type="text"
                      value={filter.value}
                      onChange={(e) => updateFilter(filter.id, 'value', e.target.value)}
                      placeholder={filter.operator === 'BETWEEN' ? 'value1,value2' : 'Value'}
                      className="input flex-1"
                    />
                  )}
                  <button
                    onClick={() => removeFilter(filter.id)}
                    className="text-red-600 hover:text-red-700 p-1"
                    title="Remove filter"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* GROUP BY */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium">GROUP BY</label>
                <button
                  onClick={addGroupBy}
                  className="text-sm bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700 flex items-center space-x-1"
                  data-testid="add-groupby"
                >
                  <Plus className="w-3 h-3" />
                  <span>Add</span>
                </button>
              </div>
              <div className="space-y-2">
                {groupBy.map(g => (
                  <div key={g.id} className="flex items-center space-x-2">
                    <select
                      value={g.column}
                      onChange={(e) => updateGroupBy(g.id, e.target.value)}
                      className="input flex-1 text-sm"
                    >
                      {getAllColumns().map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                    <button
                      onClick={() => removeGroupBy(g.id)}
                      className="text-red-600 hover:text-red-700 p-1"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* ORDER BY */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium">ORDER BY</label>
                <button
                  onClick={addOrderBy}
                  className="text-sm bg-primary-600 text-white px-2 py-1 rounded hover:bg-primary-700 flex items-center space-x-1"
                  data-testid="add-orderby"
                >
                  <Plus className="w-3 h-3" />
                  <span>Add</span>
                </button>
              </div>
              <div className="space-y-2">
                {orderBy.map(o => (
                  <div key={o.id} className="flex items-center space-x-2">
                    <select
                      value={o.column}
                      onChange={(e) => updateOrderBy(o.id, 'column', e.target.value)}
                      className="input flex-1 text-sm"
                    >
                      {getAllColumns().map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                    <select
                      value={o.direction}
                      onChange={(e) => updateOrderBy(o.id, 'direction', e.target.value as 'ASC' | 'DESC')}
                      className="input w-20 text-sm"
                    >
                      <option value="ASC">ASC</option>
                      <option value="DESC">DESC</option>
                    </select>
                    <button
                      onClick={() => removeOrderBy(o.id)}
                      className="text-red-600 hover:text-red-700 p-1"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* LIMIT */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <label className="block text-sm font-medium mb-2">LIMIT</label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
              className="input w-32"
              min="1"
              max="10000"
            />
          </div>

          {/* Generated SQL Preview */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">Generated SQL</label>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedSQL);
                  alert('SQL copied to clipboard!');
                }}
                className="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1"
              >
                <Copy className="w-4 h-4" />
                <span>Copy</span>
              </button>
            </div>
            <pre className="bg-white dark:bg-gray-800 p-3 rounded border border-gray-200 dark:border-gray-700 text-sm font-mono overflow-x-auto">
              {generatedSQL || 'Build your query above to see generated SQL'}
            </pre>
          </div>
        </>
      )}
    </div>
  );
};

export default VisualQueryBuilder;
