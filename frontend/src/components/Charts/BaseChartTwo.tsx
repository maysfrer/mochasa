import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import TableTwo from '../Tables/TableTwo';
import { preventDeletion, isClearable } from '@common/utils';

const BaseChartTwo: React.FC = () => {
  const [bodegas, setBodegas] = useState<string[]>([]);
  const [skus, setSkus] = useState<string[]>([]);
  const [selectedBodega, setSelectedBodega] = useState<string[]>([]);
  const [selectedSku, setSelectedSku] = useState<string[]>([]);

  // Fetch bodegas
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
      });
    return () => {
      ignore = true;
    };
  }, []);

  // Fetch SKUs for selected bodega
  useEffect(() => {
    const fetchSkus = async () => {
      if (selectedBodega.length) {
        const query = new URLSearchParams();
        selectedBodega.forEach((b) => query.append('bodega', b));

        const response = await fetch(
          `${
            import.meta.env.VITE_API_URL
          }/api/available-skus?${query.toString()}`,
        );
        const json = await response.json();
        const skuList = json.data;
        setSkus(skuList);
        if (skuList.length) {
          setSelectedSku([]); // default to all
        }
      }
    };

    fetchSkus();
  }, [selectedBodega]);

  const bodegaOptions = bodegas.map((b) => ({ value: b, label: b }));
  const skuOptions = skus.map((s) => ({ value: s, label: s }));

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

        {/* SKU Multi-select */}
        <Select
          isMulti
          value={selectedSku.map((sku) => ({ value: sku, label: sku }))}
          onChange={preventDeletion(selectedSku, setSelectedSku, true)}
          options={skuOptions}
          className="mb-3"
          placeholder={
            selectedSku.length === 0 ? 'Todos los SKUs' : 'Select SKUs'
          }
          isOptionDisabled={(option) =>
            selectedSku.length >= 4 && !selectedSku.includes(option.value)
          }
          isClearable={isClearable(selectedSku, true)}
        />
      </div>

      <div className="pt-0">
        <TableTwo selectedBodega={selectedBodega} selectedSku={selectedSku} />
      </div>
    </div>
  );
};

export default BaseChartTwo;
