import React, { useEffect, useState, useRef } from 'react';
import { Plus, FileText, Play, Trash2, Download, Clock, Database, Moon, Sun, History, Edit, Eye, Wand2, Code, BarChart3 } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { format as formatSQL } from 'sql-formatter';
import { queryService } from '../services/queryService';
import { datasourceService } from '../services/datasourceService';
import { Query, QueryResult, DataSource } from '../types';
import VisualQueryBuilder, { VisualQueryConfig } from '../components/VisualQueryBuilder';

interface QueryHistoryItem {
  sql: string;
  timestamp: Date;
  executionTime: number;
  rowCount: number;
}

const QueriesPage: React.FC = () => {
  const [queries, setQueries] = useState<Query[]>([]);
  const [datasources, setDatasources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [darkMode, setDarkMode] = useState(false);
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage] = useState(50);
  const [editingQuery, setEditingQuery] = useState<Query | null>(null);
  const [viewingQuery, setViewingQuery] = useState<Query | null>(null);
  const [viewQueryResult, setViewQueryResult] = useState<QueryResult | null>(null);
  const [viewQueryExecuting, setViewQueryExecuting] = useState(false);
  const editorRef = useRef<any>(null);
  const [schemaCache, setSchemaCache] = useState<any>(null);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [queryMode, setQueryMode] = useState<'sql' | 'visual'>('sql');
  const [visualConfig, setVisualConfig] = useState<VisualQueryConfig | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    datasource_id: '',
    sql_query: 'SELECT * FROM customers LIMIT 10;'
  });

  useEffect(() => {
    loadData();
    // Load query history from localStorage
    const savedHistory = localStorage.getItem('queryHistory');
    if (savedHistory) {
      setQueryHistory(JSON.parse(savedHistory).map((item: any) => ({
        ...item,
        timestamp: new Date(item.timestamp)
      })));
    }
  }, []);

  const loadData = async () => {
    try {
      const [queriesData, datasourcesData] = await Promise.all([
        queryService.list(),
        datasourceService.list()
      ]);
      setQueries(queriesData);
      setDatasources(datasourcesData);
      if (datasourcesData.length > 0) {
        setFormData(prev => ({ ...prev, datasource_id: datasourcesData[0].id }));
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSchema = async (datasourceId: string) => {
    if (!datasourceId) return;
    setLoadingSchema(true);
    try {
      const schema = await datasourceService.getSchema(datasourceId);
      setSchemaCache(schema);
      return schema;
    } catch (error) {
      console.error('Failed to load schema:', error);
    } finally {
      setLoadingSchema(false);
    }
  };

  const formatQuery = () => {
    if (!formData.sql_query) return;
    try {
      const formatted = formatSQL(formData.sql_query, {
        language: 'sql',
        tabWidth: 2,
        keywordCase: 'upper',
        linesBetweenQueries: 2,
      });
      setFormData({ ...formData, sql_query: formatted });
    } catch (error) {
      console.error('Failed to format SQL:', error);
    }
  };

  const saveQueryToHistory = (sql: string, executionTime: number, rowCount: number) => {
    const historyItem: QueryHistoryItem = {
      sql,
      timestamp: new Date(),
      executionTime,
      rowCount
    };
    const newHistory = [historyItem, ...queryHistory].slice(0, 20);
    setQueryHistory(newHistory);
    localStorage.setItem('queryHistory', JSON.stringify(newHistory));
  };

  const handleExecute = async () => {
    setExecuting(true);
    setResult(null);
    const startTime = performance.now();
    try {
      const queryResult = await queryService.execute({
        datasource_id: formData.datasource_id,
        sql_query: formData.sql_query,
        limit: 1000
      });
      const executionTime = (performance.now() - startTime) / 1000;
      setResult({
        ...queryResult,
        execution_time: executionTime
      });
      saveQueryToHistory(formData.sql_query, executionTime, queryResult.total_rows);
      setCurrentPage(1);
      setSortColumn(null);
    } catch (error: any) {
      alert(`Query execution failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const queryData: any = {
        name: formData.name,
        description: formData.description,
        datasource_id: formData.datasource_id,
        query_type: queryMode,
        sql_query: formData.sql_query
      };

      // Include visual config if in visual mode
      if (queryMode === 'visual' && visualConfig) {
        queryData.query_config = visualConfig;
      }

      if (editingQuery) {
        // Update existing query
        await queryService.update(editingQuery.id, queryData);
      } else {
        // Create new query
        await queryService.create(queryData);
      }
      
      setShowModal(false);
      setEditingQuery(null);
      loadData();
      setFormData({
        name: '',
        description: '',
        datasource_id: datasources[0]?.id || '',
        sql_query: 'SELECT * FROM customers LIMIT 10;'
      });
      setResult(null);
      setVisualConfig(null);
      setQueryMode('sql');
    } catch (error) {
      console.error('Failed to save query:', error);
      alert('Failed to save query');
    }
  };

  const handleView = async (query: Query) => {
    setViewingQuery(query);
    setViewQueryResult(null);
    // Auto-execute the query to show results
    setViewQueryExecuting(true);
    try {
      const queryResult = await queryService.execute({
        query_id: query.id,
        limit: 100
      });
      setViewQueryResult(queryResult);
    } catch (error: any) {
      console.error('Failed to execute query:', error);
      setViewQueryResult({
        columns: [],
        rows: [],
        total_rows: 0,
        execution_time: 0,
        error: error.response?.data?.detail || error.message
      } as any);
    } finally {
      setViewQueryExecuting(false);
    }
  };

  const handleEdit = async (query: Query) => {
    setEditingQuery(query);
    setFormData({
      name: query.name,
      description: query.description || '',
      datasource_id: query.datasource_id,
      sql_query: query.sql_query || 'SELECT * FROM customers LIMIT 10;'
    });
    setResult(null);
    
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

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this query?')) {
      try {
        await queryService.delete(id);
        loadData();
      } catch (error) {
        console.error('Failed to delete query:', error);
      }
    }
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Add keyboard shortcut for query execution (Ctrl+Enter / Cmd+Enter)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      handleExecute();
    });

    // Add keyboard shortcut for SQL formatting (Shift+Alt+F)
    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
      formatQuery();
    });

    // Register SQL auto-completion provider
    monaco.languages.registerCompletionItemProvider('sql', {
      triggerCharacters: ['.', ' '],
      provideCompletionItems: (model: any, position: any) => {
        const suggestions: any[] = [];
        
        // Add table names from schema
        if (schemaCache && schemaCache.tables) {
          schemaCache.tables.forEach((table: any) => {
            suggestions.push({
              label: table.table_name,
              kind: monaco.languages.CompletionItemKind.Class,
              insertText: table.table_name,
              detail: 'Table',
              documentation: `Table: ${table.table_name}`,
            });

            // Add column names with table prefix
            if (table.columns) {
              table.columns.forEach((column: any) => {
                suggestions.push({
                  label: `${table.table_name}.${column.column_name}`,
                  kind: monaco.languages.CompletionItemKind.Field,
                  insertText: `${table.table_name}.${column.column_name}`,
                  detail: `${column.data_type}`,
                  documentation: `Column: ${column.column_name} (${column.data_type})`,
                });

                // Also add column names without table prefix
                suggestions.push({
                  label: column.column_name,
                  kind: monaco.languages.CompletionItemKind.Field,
                  insertText: column.column_name,
                  detail: `${table.table_name}.${column.data_type}`,
                  documentation: `Column: ${column.column_name} from ${table.table_name}`,
                });
              });
            }
          });
        }

        // Add common SQL keywords
        const keywords = [
          'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN',
          'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'OFFSET', 'INSERT INTO',
          'UPDATE', 'DELETE', 'CREATE TABLE', 'ALTER TABLE', 'DROP TABLE',
          'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'DISTINCT', 'AS', 'ON',
          'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE', 'IS NULL', 'IS NOT NULL'
        ];

        keywords.forEach(keyword => {
          suggestions.push({
            label: keyword,
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: keyword,
            detail: 'SQL Keyword',
          });
        });

        // Add SQL functions
        const functions = [
          'COUNT()', 'SUM()', 'AVG()', 'MIN()', 'MAX()', 'ROUND()',
          'UPPER()', 'LOWER()', 'CONCAT()', 'SUBSTRING()', 'TRIM()',
          'NOW()', 'CURRENT_DATE', 'CURRENT_TIMESTAMP', 'DATE_FORMAT()',
          'COALESCE()', 'CAST()', 'CASE WHEN THEN ELSE END'
        ];

        functions.forEach(func => {
          suggestions.push({
            label: func,
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: func,
            detail: 'SQL Function',
          });
        });

        return { suggestions };
      },
    });
  };

  const handleSort = (columnIndex: number) => {
    if (sortColumn === columnIndex) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
    setCurrentPage(1);
  };

  const getSortedRows = () => {
    if (!result || sortColumn === null) return result?.rows || [];
    
    const sorted = [...result.rows].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      
      if (aVal === null) return 1;
      if (bVal === null) return -1;
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      
      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
    
    return sorted;
  };

  const getPaginatedRows = () => {
    const sorted = getSortedRows();
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return sorted.slice(startIndex, endIndex);
  };

  const totalPages = result ? Math.ceil(result.rows.length / rowsPerPage) : 0;

  const exportToCSV = () => {
    if (!result) return;
    
    const csv = [
      result.columns.join(','),
      ...result.rows.map(row => 
        row.map(cell => {
          const str = cell === null ? '' : String(cell);
          return str.includes(',') ? `"${str}"` : str;
        }).join(',')
      )
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query-results-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToJSON = () => {
    if (!result) return;
    
    const data = result.rows.map(row => {
      const obj: any = {};
      result.columns.forEach((col, idx) => {
        obj[col] = row[idx];
      });
      return obj;
    });
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `query-results-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const loadHistoryQuery = (sql: string) => {
    setFormData({ ...formData, sql_query: sql });
    setShowHistory(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">SQL Editor</h1>
          <p className="text-gray-600 mt-2">Write and execute SQL queries with advanced features</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center space-x-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
            data-testid="query-history-button"
          >
            <History className="w-5 h-5" />
            <span>History</span>
          </button>
          <button
            onClick={() => {
              setEditingQuery(null);
              const defaultDatasourceId = datasources[0]?.id || '';
              setFormData({
                name: '',
                description: '',
                datasource_id: defaultDatasourceId,
                sql_query: 'SELECT * FROM customers LIMIT 10;'
              });
              setResult(null);
              setShowModal(true);
              if (defaultDatasourceId) {
                loadSchema(defaultDatasourceId);
              }
            }}
            disabled={datasources.length === 0}
            className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            data-testid="create-query-button"
          >
            <Plus className="w-5 h-5" />
            <span>New Query</span>
          </button>
        </div>
      </div>

      {datasources.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg mb-6">
          Please add a data source first before creating queries.
        </div>
      )}

      {/* Query History Sidebar */}
      {showHistory && queryHistory.length > 0 && (
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
            <History className="w-5 h-5 mr-2" />
            Recent Query History
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {queryHistory.map((item, idx) => (
              <div
                key={idx}
                onClick={() => loadHistoryQuery(item.sql)}
                className="p-3 border border-gray-200 rounded hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="text-xs font-mono text-gray-600 truncate mb-1">{item.sql}</div>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{item.timestamp.toLocaleString()}</span>
                  <span>{item.executionTime.toFixed(3)}s • {item.rowCount} rows</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : queries.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No saved queries yet</h3>
          <p className="text-gray-600 mb-4">Start by creating your first query</p>
          {datasources.length > 0 && (
            <button
              onClick={() => setShowModal(true)}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
            >
              Create Query
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {queries.map((query) => (
            <div key={query.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{query.name}</h3>
                    <p className="text-sm text-gray-500">{query.query_type}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleView(query)}
                    className="text-gray-600 hover:text-gray-700"
                    title="View query"
                    data-testid={`view-query-${query.id}`}
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleEdit(query)}
                    className="text-blue-600 hover:text-blue-700"
                    title="Edit query"
                    data-testid={`edit-query-${query.id}`}
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(query.id)}
                    className="text-red-600 hover:text-red-700"
                    title="Delete query"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {query.description && (
                <p className="text-sm text-gray-600 mb-3">{query.description}</p>
              )}
              <div className="bg-gray-50 rounded p-2 mb-3">
                <code className="text-xs text-gray-700 break-all">{query.sql_query?.substring(0, 100)}...</code>
              </div>
              <div className="text-sm text-gray-500">
                <p>Created: {new Date(query.created_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Enhanced SQL Editor Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[95vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {editingQuery ? 'Edit Query' : 'SQL Editor'}
                </h2>
                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-lg hover:bg-gray-100"
                  title="Toggle theme"
                >
                  {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
              </div>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Query Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="input"
                      placeholder="My Query"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Database className="w-4 h-4 inline mr-1" />
                      Data Source
                    </label>
                    <select
                      value={formData.datasource_id}
                      onChange={(e) => {
                        const newDatasourceId = e.target.value;
                        setFormData({ ...formData, datasource_id: newDatasourceId });
                        loadSchema(newDatasourceId);
                      }}
                      className="input"
                      required
                    >
                      {datasources.map((ds) => (
                        <option key={ds.id} value={ds.id}>
                          {ds.name} ({ds.type})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input"
                    placeholder="Query description"
                  />
                </div>

                {/* Query Mode Toggle */}
                <div className="flex items-center space-x-4 p-3 bg-gray-100 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Query Mode:</span>
                  <button
                    type="button"
                    onClick={() => setQueryMode('sql')}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      queryMode === 'sql' 
                        ? 'bg-primary-600 text-white' 
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                    data-testid="sql-mode-button"
                  >
                    <Code className="w-4 h-4" />
                    <span>SQL Editor</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setQueryMode('visual');
                      if (formData.datasource_id && !schemaCache) {
                        loadSchema(formData.datasource_id);
                      }
                    }}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      queryMode === 'visual' 
                        ? 'bg-primary-600 text-white' 
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                    data-testid="visual-mode-button"
                  >
                    <BarChart3 className="w-4 h-4" />
                    <span>Visual Builder</span>
                  </button>
                </div>

                {/* SQL Editor Mode */}
                {queryMode === 'sql' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">SQL Query</label>
                      <div className="flex items-center space-x-2">
                        {loadingSchema && (
                          <span className="text-xs text-gray-500 flex items-center">
                            <div className="animate-spin rounded-full h-3 w-3 border-b border-primary-600 mr-1"></div>
                            Loading schema...
                          </span>
                        )}
                        <button
                          type="button"
                          onClick={formatQuery}
                          className="flex items-center space-x-1 text-sm text-primary-600 hover:text-primary-700 px-3 py-1 rounded border border-primary-300 hover:bg-primary-50"
                          title="Format SQL (Shift+Alt+F)"
                          data-testid="format-sql-button"
                        >
                          <Wand2 className="w-4 h-4" />
                          <span>Format</span>
                        </button>
                      </div>
                    </div>
                    <div className="border border-gray-300 rounded-lg overflow-hidden">
                      <Editor
                        height="350px"
                        defaultLanguage="sql"
                        value={formData.sql_query}
                        onChange={(value) => setFormData({ ...formData, sql_query: value || '' })}
                        onMount={handleEditorDidMount}
                        theme={darkMode ? 'vs-dark' : 'light'}
                        options={{
                          minimap: { enabled: true },
                          fontSize: 14,
                          lineNumbers: 'on',
                          scrollBeyondLastLine: false,
                          automaticLayout: true,
                          tabSize: 2,
                          wordWrap: 'on',
                          formatOnPaste: true,
                          formatOnType: true,
                          quickSuggestions: true,
                          suggestOnTriggerCharacters: true,
                          acceptSuggestionOnEnter: 'on',
                          tabCompletion: 'on',
                          suggest: {
                            showKeywords: true,
                            showSnippets: true,
                            showFunctions: true,
                          },
                          parameterHints: {
                            enabled: true,
                          },
                          folding: true,
                          bracketPairColorization: {
                            enabled: true,
                          },
                        }}
                      />
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      💡 Tip: Press <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded">Ctrl+Enter</kbd> to execute query, 
                      <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded ml-1">Shift+Alt+F</kbd> to format
                    </div>
                  </div>
                )}

                {/* Visual Query Builder Mode */}
                {queryMode === 'visual' && (
                  <div className="max-h-[500px] overflow-y-auto">
                    <VisualQueryBuilder
                      schema={schemaCache}
                      onQueryGenerated={(sql) => setFormData({ ...formData, sql_query: sql })}
                      darkMode={darkMode}
                      initialConfig={visualConfig}
                      onConfigChange={(config) => setVisualConfig(config)}
                    />
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleExecute}
                  disabled={executing || !formData.datasource_id}
                  className="w-full flex items-center justify-center space-x-2 border-2 border-primary-600 text-primary-600 px-4 py-3 rounded-lg hover:bg-primary-50 transition-colors disabled:opacity-50 font-medium"
                  data-testid="execute-query-button"
                >
                  <Play className="w-5 h-5" />
                  <span>{executing ? 'Executing...' : 'Execute Query'}</span>
                </button>

                {result && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    <div className="mb-4 flex justify-between items-center">
                      <div className="flex items-center space-x-4">
                        <span className="text-sm font-medium text-gray-700 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {result.execution_time.toFixed(3)}s
                        </span>
                        <span className="text-sm font-medium text-gray-700">
                          {result.total_rows} rows
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          type="button"
                          onClick={exportToCSV}
                          className="flex items-center space-x-1 text-sm bg-green-600 text-white px-3 py-1.5 rounded hover:bg-green-700"
                        >
                          <Download className="w-4 h-4" />
                          <span>CSV</span>
                        </button>
                        <button
                          type="button"
                          onClick={exportToJSON}
                          className="flex items-center space-x-1 text-sm bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700"
                        >
                          <Download className="w-4 h-4" />
                          <span>JSON</span>
                        </button>
                      </div>
                    </div>
                    
                    <div className="overflow-x-auto max-h-96 overflow-y-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            {result.columns.map((col, idx) => (
                              <th
                                key={idx}
                                onClick={() => handleSort(idx)}
                                className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                              >
                                <div className="flex items-center space-x-1">
                                  <span>{col}</span>
                                  {sortColumn === idx && (
                                    <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>
                                  )}
                                </div>
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {getPaginatedRows().map((row, rowIdx) => (
                            <tr key={rowIdx} className="hover:bg-gray-50">
                              {row.map((cell, cellIdx) => (
                                <td key={cellIdx} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                                  {cell !== null ? String(cell) : <span className="text-gray-400 italic">null</span>}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    {totalPages > 1 && (
                      <div className="mt-4 flex items-center justify-between">
                        <div className="text-sm text-gray-700">
                          Page {currentPage} of {totalPages}
                        </div>
                        <div className="flex space-x-2">
                          <button
                            type="button"
                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                            disabled={currentPage === 1}
                            className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                          >
                            Previous
                          </button>
                          <button
                            type="button"
                            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                            disabled={currentPage === totalPages}
                            className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                          >
                            Next
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
                  >
                    {editingQuery ? 'Update Query' : 'Save Query'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setEditingQuery(null);
                      setResult(null);
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* View Query Modal (Read-only with Results) */}
      {viewingQuery && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-6xl w-full max-h-[95vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{viewingQuery.name}</h2>
                  {viewingQuery.description && (
                    <p className="text-gray-600 mt-1">{viewingQuery.description}</p>
                  )}
                </div>
                <button
                  onClick={() => {
                    setViewingQuery(null);
                    setViewQueryResult(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                  data-testid="close-view-modal"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Database className="w-4 h-4 inline mr-1" />
                    Data Source
                  </label>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-900">
                      {datasources.find(ds => ds.id === viewingQuery.datasource_id)?.name || 'Unknown'}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">SQL Query</label>
                  <div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
                    <pre className="text-sm text-gray-900 font-mono whitespace-pre-wrap">
                      {viewingQuery.sql_query}
                    </pre>
                  </div>
                </div>

                <div className="text-sm text-gray-500">
                  <p>Created: {new Date(viewingQuery.created_at).toLocaleString()}</p>
                  <p>Type: {viewingQuery.query_type}</p>
                </div>

                {/* Query Results Section */}
                <div className="border-t pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">Query Results</h3>
                    {viewQueryResult && !viewQueryExecuting && (
                      <div className="flex items-center space-x-4">
                        <span className="text-sm font-medium text-gray-700 flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {viewQueryResult.execution_time?.toFixed(3)}s
                        </span>
                        <span className="text-sm font-medium text-gray-700">
                          {viewQueryResult.total_rows} rows
                        </span>
                      </div>
                    )}
                  </div>

                  {viewQueryExecuting ? (
                    <div className="flex items-center justify-center h-48 bg-gray-50 rounded-lg">
                      <div className="text-center">
                        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto mb-3"></div>
                        <p className="text-gray-600">Executing query...</p>
                      </div>
                    </div>
                  ) : viewQueryResult ? (
                    (viewQueryResult as any).error ? (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <p className="text-red-800 font-medium">Failed to execute query</p>
                        <p className="text-sm text-red-600 mt-1">{(viewQueryResult as any).error}</p>
                      </div>
                    ) : (
                      <div className="border border-gray-200 rounded-lg overflow-hidden">
                        <div className="overflow-x-auto max-h-96 overflow-y-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50 sticky top-0">
                              <tr>
                                {viewQueryResult.columns.map((col, idx) => (
                                  <th
                                    key={idx}
                                    className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                                  >
                                    {col}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {viewQueryResult.rows.map((row, rowIdx) => (
                                <tr key={rowIdx} className="hover:bg-gray-50">
                                  {row.map((cell, cellIdx) => (
                                    <td key={cellIdx} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                                      {cell !== null ? String(cell) : <span className="text-gray-400 italic">null</span>}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )
                  ) : null}
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={() => {
                      setViewingQuery(null);
                      setViewQueryResult(null);
                      handleEdit(viewingQuery);
                    }}
                    className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium"
                    data-testid="edit-from-view-button"
                  >
                    Edit Query
                  </button>
                  <button
                    onClick={() => {
                      setViewingQuery(null);
                      setViewQueryResult(null);
                    }}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueriesPage;