import React, { useState } from 'react';
import { Table, Play, AlertCircle, Info, Download } from 'lucide-react';
import analyticsService, { PivotTableRequest } from '../../services/analyticsService';

interface Props {
  dataSources: Array<{ id: string; name: string; type: string }>;
}

interface PivotResult {
  pivot_data: any[];
  row_labels: string[];
  column_labels: string[];
  grand_total: number;
}

const PivotTable: React.FC<Props> = ({ dataSources }) => {
  const [selectedDatasource, setSelectedDatasource] = useState('');
  const [query, setQuery] = useState('');
  const [rows, setRows] = useState<string[]>(['']);
  const [columns, setColumns] = useState<string[]>(['']);
  const [valueColumn, setValueColumn] = useState('');
  const [aggFunc, setAggFunc] = useState<'sum' | 'mean' | 'count' | 'min' | 'max' | 'median' | 'std'>('sum');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PivotResult | null>(null);
  const [error, setError] = useState('');

  const handleAddRow = () => setRows([...rows, '']);
  const handleAddColumn = () => setColumns([...columns, '']);

  const handleRemoveRow = (index: number) => {
    if (rows.length > 1) setRows(rows.filter((_, i) => i !== index));
  };

  const handleRemoveColumn = (index: number) => {
    if (columns.length > 1) setColumns(columns.filter((_, i) => i !== index));
  };

  const handleRowChange = (index: number, value: string) => {
    const newRows = [...rows];
    newRows[index] = value;
    setRows(newRows);
  };

  const handleColumnChange = (index: number, value: string) => {
    const newColumns = [...columns];
    newColumns[index] = value;
    setColumns(newColumns);
  };

  const handleGeneratePivot = async () => {
    if (!selectedDatasource || !query || !valueColumn) {
      setError('Please select data source, enter query, and specify value column');
      return;
    }

    const validRows = rows.filter(r => r.trim() !== '');
    const validColumns = columns.filter(c => c.trim() !== '');

    if (validRows.length === 0 || validColumns.length === 0) {
      setError('Please specify at least one row and one column');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const request: PivotTableRequest = {
        datasource_id: selectedDatasource,
        query: query,
        rows: validRows,
        columns: validColumns,
        values: valueColumn,
        aggfunc: aggFunc
      };

      const data = await analyticsService.pivotTable(request);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate pivot table');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleQuery = () => {
    setQuery('SELECT category, region, product_name, sales FROM sales_data');
    setRows(['category']);
    setColumns(['region']);
    setValueColumn('sales');
    setAggFunc('sum');
  };

  const exportToCSV = () => {
    if (!result) return;

    // Create CSV content
    let csv = 'Row,' + result.column_labels.join(',') + '\n';
    result.pivot_data.forEach((row: any, index: number) => {
      const rowLabel = result.row_labels[index] || '';
      const values = result.column_labels.map((col: string) => row[col] || 0);
      csv += rowLabel + ',' + values.join(',') + '\n';
    });
    csv += 'Grand Total,' + result.grand_total + '\n';

    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pivot_table.csv';
    a.click();
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Table className="w-6 h-6 text-blue-600" />
          Pivot Tables
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Interactive pivot tables for dynamic data aggregation and slicing
        </p>
      </div>

      {/* Configuration */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration</h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Data Source */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data Source *
            </label>
            <select
              value={selectedDatasource}
              onChange={(e) => setSelectedDatasource(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              data-testid="datasource-select"
            >
              <option value="">Select a data source...</option>
              {dataSources.map((ds) => (
                <option key={ds.id} value={ds.id}>
                  {ds.name} ({ds.type})
                </option>
              ))}
            </select>
          </div>

          {/* Aggregation Function */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Aggregation Function
            </label>
            <select
              value={aggFunc}
              onChange={(e) => setAggFunc(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              data-testid="aggfunc-select"
            >
              <option value="sum">Sum</option>
              <option value="mean">Average (Mean)</option>
              <option value="count">Count</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
              <option value="median">Median</option>
              <option value="std">Standard Deviation</option>
            </select>
          </div>
        </div>

        {/* Query */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              SQL Query *
            </label>
            <button
              onClick={loadSampleQuery}
              className="text-xs text-blue-600 hover:text-blue-700"
            >
              Load Sample
            </button>
          </div>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            rows={3}
            placeholder="SELECT column1, column2, value_column FROM table"
            data-testid="query-input"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          {/* Row Fields */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Row Fields *
            </label>
            {rows.map((row, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={row}
                  onChange={(e) => handleRowChange(index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="row_column"
                  data-testid={`row-input-${index}`}
                />
                {rows.length > 1 && (
                  <button
                    onClick={() => handleRemoveRow(index)}
                    className="px-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
            <button
              onClick={handleAddRow}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              + Add Row Field
            </button>
          </div>

          {/* Column Fields */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Column Fields *
            </label>
            {columns.map((col, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={col}
                  onChange={(e) => handleColumnChange(index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="column_field"
                  data-testid={`column-input-${index}`}
                />
                {columns.length > 1 && (
                  <button
                    onClick={() => handleRemoveColumn(index)}
                    className="px-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
            <button
              onClick={handleAddColumn}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              + Add Column Field
            </button>
          </div>

          {/* Value Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Value Field *
            </label>
            <input
              type="text"
              value={valueColumn}
              onChange={(e) => setValueColumn(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="value_column"
              data-testid="value-input"
            />
            <p className="text-xs text-gray-500 mt-1">
              Numeric column to aggregate
            </p>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGeneratePivot}
          disabled={loading || !selectedDatasource || !query}
          className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
          data-testid="generate-button"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
              Generating...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Generate Pivot Table
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {!result && !error && !loading && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <Info className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600">Configure and generate a pivot table to see results</p>
        </div>
      )}

      {result && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Pivot Table Results</h3>
            <button
              onClick={exportToCSV}
              className="flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg"
              data-testid="export-button"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>

          <div className="p-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Row \ Column
                  </th>
                  {result.column_labels.map((col, index) => (
                    <th
                      key={index}
                      className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {result.pivot_data.map((row, rowIndex) => (
                  <tr key={rowIndex} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {result.row_labels[rowIndex]}
                    </td>
                    {result.column_labels.map((col, colIndex) => (
                      <td key={colIndex} className="px-4 py-3 text-sm text-right text-gray-700">
                        {typeof row[col] === 'number' ? row[col].toLocaleString() : (row[col] || '-')}
                      </td>
                    ))}
                  </tr>
                ))}
                <tr className="bg-blue-50 font-bold">
                  <td className="px-4 py-3 text-sm text-gray-900">
                    Grand Total
                  </td>
                  <td
                    colSpan={result.column_labels.length}
                    className="px-4 py-3 text-sm text-right text-gray-900"
                  >
                    {result.grand_total.toLocaleString()}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="p-4 bg-gray-50 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <span className="font-medium">Aggregation:</span> {aggFunc.toUpperCase()} of {valueColumn}
            </p>
            <p className="text-sm text-gray-600 mt-1">
              <span className="font-medium">Dimensions:</span> {result.row_labels.length} rows × {result.column_labels.length} columns
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PivotTable;