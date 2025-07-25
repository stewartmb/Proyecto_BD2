import React, { useState } from 'react';
import SQLEditor from './SQLEditor';
import Results from './results/Results';
import ResizableLayout from './ResizableLayout';
import { useQueryUrl } from '../contexts/QueryUrlContext';

interface QueryResult {
    data: any[] | null;
    columns: string[] | null;
    columns_types: string[] | null;
    table: string | null;
    message: string | null;
    error: string | null;
    details?: string | null;
}

interface Props {
    queryResult: QueryResult;
    onRunQuery: (query: string) => void;
}

const ResizablePanel: React.FC<Props> = ({ queryResult, onRunQuery }) => {
    const [query, setQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [queryHistory, setQueryHistory] = useState<string[]>([]);

    const handleRunQuery = async (sql: string) => {
        setIsLoading(true);
        try {
            await onRunQuery(sql);
            if (!queryHistory.includes(sql)) {
                setQueryHistory(prev => [sql, ...prev].slice(0, 50));
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleHistorySelect = (selectedQuery: string) => {
        setQuery(selectedQuery);
    };

    console.log("🟡 Props passed to <Results />:", {
    table: queryResult.table,
    columns: queryResult.columns,
    columns_types: queryResult.columns_types,
    data: queryResult.data,
    message: queryResult.message,
    error: queryResult.error,
    details: queryResult.details,
    });

    return (
        <ResizableLayout
            topContent={
                <SQLEditor
                    onRun={handleRunQuery}
                    isLoading={isLoading}
                    query={query}
                    onQueryChange={setQuery}
                />
            }
            bottomContent={
                <Results
                    data={queryResult.data}
                    columns={queryResult.columns || []}
                    columns_types={queryResult.columns_types || []}
                    table={queryResult.table}
                    message={queryResult.message}
                    error={queryResult.error}
                    details={queryResult.details}
                    history={queryHistory}
                    onSelectHistory={handleHistorySelect}
                    isLoading={isLoading}
                />
            }
        />
    );
};

export default ResizablePanel;