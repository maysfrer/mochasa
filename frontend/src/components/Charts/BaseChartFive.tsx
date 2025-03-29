import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import TableFive from '../Tables/TableFive';

const BaseChartFive: React.FC = () => {
  const [bodegas, setBodegas] = useState<string[]>([]);
  const [selectedBodega, setSelectedBodega] = useState<string[]>([]);

  useEffect(() => {
    let ignore = false;
    fetch(`${import.meta.env.VITE_API_URL}/api/available-bodegas`)
      .then((response) => response.json())
      .then((json) => {
        if (!ignore) {
          const bodegas = json.data;
          setBodegas(bodegas);
          if (bodegas.length) {
            setSelectedBodega([bodegas[0]]);
          }
        }
      })
      .catch((error) => {
        console.error('Error fetching bodegas:', error);
      });
    return () => {
      ignore = true;
    };
  }, []);

  const bodegaOptions = bodegas.map((bodega) => ({
    value: bodega,
    label: bodega,
  }));

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-default dark:border-strokedark dark:bg-boxdark sm:px-7.5 xl:col-span-8">
      <div className="col-span-4 mb-6">
        {/* Bodega Select */}
        <Select
          value={
            selectedBodega.length > 0
              ? { value: selectedBodega[0], label: selectedBodega[0] }
              : null
          }
          onChange={(e) => setSelectedBodega(e ? [e.value] : [])}
          options={bodegaOptions}
          className="mb-3"
          placeholder="Select Bodega"
        />
      </div>

      <div>
        <TableFive selectedBodega={selectedBodega} />
      </div>
    </div>
  );
};

export default BaseChartFive;
