import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import TableFour from '../Tables/TableFour';
import { preventDeletion, isClearable } from '@common/utils';

const BaseChartFour: React.FC = () => {
  const [bodegas, setBodegas] = useState<string[]>([]);
  const [skus, setSkus] = useState<string[]>([]);
  const [selectedBodega, setSelectedBodega] = useState<string[]>([]);
  const [selectedSku, setSelectedSku] = useState<string[]>([]);

  // Fetch available bodegas
  useEffect(() => {
    let ignore = false;
    fetch(`${import.meta.env.VITE_API_URL}/api/available-bodegas`)
      .then((res) => res.json())
      .then((json) => {
        if (!ignore) {
          const bodegas = json.data;
          setBodegas(bodegas);
          if (bodegas.length) {
            setSelectedBodega([bodegas[0]]); // single selection as array
          }
        }
      })
      .catch((error) => console.error('Error fetching bodegas:', error));

    return () => {
      ignore = true;
    };
  }, []);

  // Fetch SKUs based on selected bodega
  useEffect(() => {
    const fetchSkus = async () => {
      if (selectedBodega.length) {
        const query = new URLSearchParams();
        selectedBodega.forEach((bodega) => query.append('bodega', bodega));

        const response = await fetch(
          `${
            import.meta.env.VITE_API_URL
          }/api/available-skus?${query.toString()}`,
        );
        const json = await response.json();
        const skuList = json.data;
        setSkus(skuList);
        setSelectedSku([]); // default = all SKUs
      }
    };

    fetchSkus();
  }, [selectedBodega]);

  const bodegaOptions = bodegas.map((b) => ({ value: b, label: b }));
  const skuOptions = skus.map((s) => ({ value: s, label: s }));

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-default dark:border-strokedark dark:bg-boxdark sm:px-7.5 xl:col-span-8">
      <div className="col-span-4 mb-6">
        {/* Bodega Select (Single) */}
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

        {/* SKU Multi-Select */}
        <Select
          isMulti
          value={selectedSku.map((sku) => ({
            value: sku,
            label: sku,
          }))}
          onChange={preventDeletion(selectedSku, setSelectedSku, true)}
          options={skuOptions}
          className="mb-3"
          placeholder={
            selectedSku.length === 0 ? 'All SKUs (default)' : 'Select SKUs'
          }
          isClearable={isClearable(selectedSku, true)}
          isOptionDisabled={(option) =>
            selectedSku.length >= 4 && !selectedSku.includes(option.value)
          }
        />
      </div>

      <div>
        <TableFour selectedBodega={selectedBodega} selectedSku={selectedSku} />
      </div>
    </div>
  );
};

export default BaseChartFour;
