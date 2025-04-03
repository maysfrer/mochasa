import React, { useState, useEffect } from 'react';

interface TableRowItem {
  index: number;
  sku: string;
  mean: number;
  clase_abc: string;
  bodega: string;
  variabilidad: string;
  costo: number;
  lead_time: number;
  h: number;
  demanda_anual: number;
  T: number;
  SS: number;
  nivel_objetivo: number;
  politica: string;
}

interface TableProps {
  selectedBodega: string[];
  selectedSku: string[];
}

const getClassificationColor = (classification: string) => {
  switch (classification) {
    case 'A':
      return 'bg-green-100 text-green-800';
    case 'B':
      return 'bg-yellow-100 text-yellow-800';
    case 'C':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const TableThree: React.FC<TableProps> = ({ selectedBodega, selectedSku }) => {
  const [tableData, setTableData] = useState({
    data: [],
    total: 0,
    page: 1,
    total_pages: 0,
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedBodega, selectedSku]);

  useEffect(() => {
    const fetchTableData = async () => {
      try {
        const query = new URLSearchParams();
        selectedBodega.forEach((bodega) => query.append('bodega', bodega));
        if (selectedSku.length > 0) {
          selectedSku.forEach((sku) => query.append('sku', sku));
        }

        const response = await fetch(
          `${
            import.meta.env.VITE_API_URL
          }/api/table-3?${query.toString()}&page=${currentPage}`,
        );

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        setTableData(data);
      } catch (error) {
        setError(
          error instanceof Error ? error.message : 'An unknown error occurred',
        );
      }
    };

    if (selectedBodega.length) {
      fetchTableData();
    }
  }, [currentPage, selectedBodega, selectedSku]);

  const handleNextPage = () => {
    if (currentPage < tableData.total_pages) {
      setCurrentPage((prevPage) => prevPage + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage((prevPage) => prevPage - 1);
    }
  };

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-lg">
        <p className="text-red-800">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-8">
      <h2 className="flex justify-center items-center text-base font-semibold text-black dark:text-white text-center">
        Revisión periódica
      </h2>
      <div className="py-0">
        <div className="-mx-4 sm:-mx-8 px-4 sm:px-8 py-4 overflow-x-auto">
          <div className="inline-block min-w-full shadow rounded-lg overflow-hidden">
            <table className="min-w-full leading-normal">
              <thead>
                <tr>
                  {[
                    'SKU',
                    'Clasificación',
                    'Consumo Promedio',
                    'Tiempo de Revisión',
                    'Lead Time',
                    'Stock de Seguridad',
                    'Nivel Objetivo',
                  ].map((header) => (
                    <th
                      key={header}
                      className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.data.map((item: TableRowItem, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      <p className="text-gray-900 whitespace-no-wrap">
                        {item.sku}
                      </p>
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      <span
                        className={`inline-block px-2 py-1 rounded-full text-xs font-semibold ${getClassificationColor(
                          item.clase_abc,
                        )}`}
                      >
                        {item.clase_abc}
                      </span>
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      {item.mean}
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      {item.T}
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      {item.lead_time}
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      {item.SS}
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                      {item.nivel_objetivo}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="px-5 py-5 bg-white border-t flex flex-col xs:flex-row items-center xs:justify-between">
              <span className="text-xs xs:text-sm text-gray-900">
                Showing Page {currentPage} of {tableData.total_pages}
              </span>
              <div className="inline-flex mt-2 xs:mt-0">
                <button
                  onClick={handlePrevPage}
                  className="text-sm bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-l disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={currentPage === 1}
                >
                  Prev
                </button>
                <button
                  onClick={handleNextPage}
                  className="text-sm bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 px-4 rounded-r disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={currentPage === tableData.total_pages}
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TableThree;
