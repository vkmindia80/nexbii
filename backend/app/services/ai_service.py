"""
AI Service for NexBII - Natural Language Query Processing
Uses Emergent LLM Key for OpenAI integration
"""
import os
import re
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

class AIService:
    """AI Service for natural language query processing and insights"""
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
    
    async def natural_language_to_sql(
        self, 
        natural_query: str, 
        schema_info: Dict[str, Any],
        database_type: str = "sqlite"
    ) -> Dict[str, Any]:
        """
        Convert natural language query to SQL
        
        Args:
            natural_query: Natural language query from user
            schema_info: Database schema information (tables, columns, types)
            database_type: Type of database (sqlite, postgresql, mysql, mongodb)
        
        Returns:
            Dict with sql_query, explanation, and confidence score
        """
        try:
            # Build schema context
            schema_context = self._build_schema_context(schema_info)
            
            # Create system message for SQL generation
            system_message = f"""You are an expert SQL query generator for {database_type} databases.
Your task is to convert natural language queries into valid SQL statements.

Database Schema:
{schema_context}

Instructions:
1. Generate ONLY valid {database_type} SQL syntax
2. Use proper JOINs when multiple tables are involved
3. Include appropriate WHERE clauses for filtering
4. Use aggregation functions (COUNT, SUM, AVG, etc.) when needed
5. Add ORDER BY and LIMIT clauses when appropriate
6. Return the response in JSON format with these fields:
   - sql_query: The generated SQL query
   - explanation: Brief explanation of what the query does
   - confidence: Confidence score (0-100)
   - tables_used: List of tables used in the query
   - potential_issues: List of any potential issues or warnings

Always return valid JSON."""

            # Create chat instance
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"nl_to_sql_{hash(natural_query)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            # Send query
            user_message = UserMessage(
                text=f"Convert this natural language query to SQL: {natural_query}"
            )
            
            response = await chat.send_message(user_message)
            
            # Parse response
            result = self._parse_ai_response(response)
            
            return {
                "success": True,
                "sql_query": result.get("sql_query", ""),
                "explanation": result.get("explanation", ""),
                "confidence": result.get("confidence", 85),
                "tables_used": result.get("tables_used", []),
                "potential_issues": result.get("potential_issues", []),
                "original_query": natural_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sql_query": None,
                "explanation": "Failed to generate SQL query",
                "confidence": 0
            }
    
    async def validate_and_suggest(
        self, 
        sql_query: str, 
        schema_info: Dict[str, Any],
        database_type: str = "sqlite"
    ) -> Dict[str, Any]:
        """
        Validate SQL query and provide suggestions for improvement
        
        Args:
            sql_query: SQL query to validate
            schema_info: Database schema information
            database_type: Type of database
        
        Returns:
            Dict with validation results and suggestions
        """
        try:
            schema_context = self._build_schema_context(schema_info)
            
            system_message = f"""You are an expert SQL validator and optimizer for {database_type} databases.
Your task is to validate SQL queries and suggest improvements.

Database Schema:
{schema_context}

Instructions:
1. Check for syntax errors
2. Verify table and column names exist in schema
3. Identify performance issues (missing indexes, cartesian products, etc.)
4. Suggest optimizations (better JOINs, WHERE clause improvements, etc.)
5. Check for security issues (SQL injection risks)
6. Return response in JSON format with:
   - is_valid: boolean
   - syntax_errors: list of syntax errors
   - schema_errors: list of schema-related errors
   - performance_issues: list of performance concerns
   - security_issues: list of security concerns
   - suggestions: list of improvement suggestions
   - optimized_query: improved version of the query (if applicable)

Always return valid JSON."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"validate_query_{hash(sql_query)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(
                text=f"Validate and analyze this SQL query:\n\n{sql_query}"
            )
            
            response = await chat.send_message(user_message)
            result = self._parse_ai_response(response)
            
            return {
                "success": True,
                "is_valid": result.get("is_valid", True),
                "syntax_errors": result.get("syntax_errors", []),
                "schema_errors": result.get("schema_errors", []),
                "performance_issues": result.get("performance_issues", []),
                "security_issues": result.get("security_issues", []),
                "suggestions": result.get("suggestions", []),
                "optimized_query": result.get("optimized_query", sql_query)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "is_valid": False
            }
    
    async def optimize_query(
        self, 
        sql_query: str, 
        schema_info: Dict[str, Any],
        execution_time: Optional[float] = None,
        database_type: str = "sqlite"
    ) -> Dict[str, Any]:
        """
        Suggest query optimizations
        
        Args:
            sql_query: SQL query to optimize
            schema_info: Database schema information
            execution_time: Current execution time in seconds (optional)
            database_type: Type of database
        
        Returns:
            Dict with optimization suggestions
        """
        try:
            schema_context = self._build_schema_context(schema_info)
            
            exec_time_info = f"\nCurrent execution time: {execution_time} seconds" if execution_time else ""
            
            system_message = f"""You are an expert SQL performance optimizer for {database_type} databases.

Database Schema:
{schema_context}
{exec_time_info}

Instructions:
1. Analyze the query for performance bottlenecks
2. Suggest specific optimizations
3. Recommend indexes if needed
4. Identify unnecessary operations
5. Suggest better query structure if applicable
6. Return response in JSON format with:
   - optimized_query: optimized version of the query
   - optimizations_applied: list of specific optimizations
   - estimated_improvement: estimated performance improvement (percentage)
   - recommended_indexes: list of recommended indexes
   - explanation: detailed explanation of changes

Always return valid JSON."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"optimize_query_{hash(sql_query)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(
                text=f"Optimize this SQL query for better performance:\n\n{sql_query}"
            )
            
            response = await chat.send_message(user_message)
            result = self._parse_ai_response(response)
            
            return {
                "success": True,
                "optimized_query": result.get("optimized_query", sql_query),
                "optimizations_applied": result.get("optimizations_applied", []),
                "estimated_improvement": result.get("estimated_improvement", 0),
                "recommended_indexes": result.get("recommended_indexes", []),
                "explanation": result.get("explanation", ""),
                "original_query": sql_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "optimized_query": sql_query
            }
    
    async def recommend_chart_type(
        self, 
        query_result: Dict[str, Any],
        sql_query: str
    ) -> Dict[str, Any]:
        """
        Recommend best chart type based on query results
        
        Args:
            query_result: Query execution results with columns and data
            sql_query: The SQL query that generated the results
        
        Returns:
            Dict with chart recommendations
        """
        try:
            # Analyze data structure
            columns = query_result.get("columns", [])
            data_sample = query_result.get("data", [])[:5]  # First 5 rows
            
            data_info = f"""
Query: {sql_query}

Columns: {', '.join(columns)}
Number of columns: {len(columns)}
Number of rows: {len(query_result.get('data', []))}
Sample data (first 5 rows):
{json.dumps(data_sample, indent=2)}
"""
            
            system_message = """You are an expert data visualization consultant.
Your task is to recommend the best chart types for visualizing query results.

Available chart types:
- line: Time series, trends over time
- bar: Horizontal comparisons, categorical data
- column: Vertical comparisons, categorical data
- area: Cumulative trends, filled time series
- pie: Proportions, parts of a whole (max 10 categories)
- donut: Proportions with center space
- scatter: Correlations, relationships between two variables
- gauge: Progress, single metric with target
- metric: KPI, single number display
- table: Raw data, detailed information
- bubble: 3D scatter with size dimension
- heatmap: Correlation matrix, intensity data
- boxplot: Statistical distribution
- treemap: Hierarchical proportions
- sunburst: Radial hierarchical data
- waterfall: Cumulative changes
- funnel: Conversion stages
- radar: Multivariate comparison
- candlestick: Financial OHLC data
- sankey: Flow between nodes

Instructions:
1. Analyze the data structure (columns, data types, relationships)
2. Consider the query intent (aggregations, time series, comparisons, etc.)
3. Recommend 1-3 most suitable chart types
4. Provide configuration suggestions for each chart
5. Return response in JSON format with:
   - primary_recommendation: The best chart type
   - chart_config: Suggested configuration for the primary chart
   - alternative_charts: List of 2 alternative chart types with configs
   - reasoning: Explanation of recommendations

Always return valid JSON."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"chart_recommend_{hash(sql_query)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(
                text=f"Recommend the best chart type for this data:\n\n{data_info}"
            )
            
            response = await chat.send_message(user_message)
            result = self._parse_ai_response(response)
            
            return {
                "success": True,
                "primary_recommendation": result.get("primary_recommendation", "table"),
                "chart_config": result.get("chart_config", {}),
                "alternative_charts": result.get("alternative_charts", []),
                "reasoning": result.get("reasoning", ""),
                "columns": columns
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "primary_recommendation": "table"
            }
    
    async def generate_insights(
        self, 
        query_result: Dict[str, Any],
        sql_query: str
    ) -> Dict[str, Any]:
        """
        Generate automated insights from query results
        
        Args:
            query_result: Query execution results
            sql_query: The SQL query that generated the results
        
        Returns:
            Dict with generated insights
        """
        try:
            columns = query_result.get("columns", [])
            data = query_result.get("data", [])
            
            # Limit data size for AI processing
            data_sample = data[:100] if len(data) > 100 else data
            
            data_info = f"""
Query: {sql_query}

Columns: {', '.join(columns)}
Number of rows: {len(data)}
Data sample:
{json.dumps(data_sample, indent=2)}
"""
            
            system_message = """You are an expert data analyst specializing in business intelligence.
Your task is to analyze query results and generate actionable insights.

Instructions:
1. Identify key patterns and trends in the data
2. Highlight significant findings (outliers, anomalies, correlations)
3. Provide business context and implications
4. Suggest follow-up questions or analyses
5. Return response in JSON format with:
   - key_insights: List of 3-5 key insights (each with title and description)
   - trends: Identified trends in the data
   - anomalies: Any unusual patterns or outliers
   - recommendations: Business recommendations based on findings
   - follow_up_questions: Suggested questions for deeper analysis

Always return valid JSON. Keep insights concise and actionable."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"insights_{hash(sql_query)}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            user_message = UserMessage(
                text=f"Generate insights from this data:\n\n{data_info}"
            )
            
            response = await chat.send_message(user_message)
            result = self._parse_ai_response(response)
            
            return {
                "success": True,
                "key_insights": result.get("key_insights", []),
                "trends": result.get("trends", []),
                "anomalies": result.get("anomalies", []),
                "recommendations": result.get("recommendations", []),
                "follow_up_questions": result.get("follow_up_questions", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "key_insights": []
            }
    
    def _build_schema_context(self, schema_info: Dict[str, Any]) -> str:
        """Build schema context string for AI"""
        if not schema_info:
            return "No schema information available"
        
        context_parts = []
        
        for table_name, table_info in schema_info.items():
            columns = table_info.get("columns", [])
            column_list = ", ".join([f"{col['name']} ({col.get('type', 'unknown')})" for col in columns])
            context_parts.append(f"Table: {table_name}\nColumns: {column_list}")
        
        return "\n\n".join(context_parts)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response, handling both JSON and text formats"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON found, return the text response
            return {"response": response}
            
        except json.JSONDecodeError:
            # Fallback: return response as-is
            return {"response": response}


# Create singleton instance
ai_service = AIService()
