import { ApexOptions } from 'apexcharts';
import React, { useState, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';
import Select from 'react-select';
import { isClearable, preventDeletion, getMinMaxValues } from '@common/utils';

const baseOptions: ApexOptions = {
  legend: {
    show: false,
    position: 'top',
    horizontalAlign: 'left',
  },
  title: {
    text: 'Consumo histórico semanal',
    align: 'center', // You can also use 'left' or 'right'
    style: {
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#333',
      fontFamily: 'Satoshi, sans-serif',
    },
  },
  colors: ['#3C50E0', '#80CAEE'],
  chart: {
    fontFamily: 'Satoshi, sans-serif',
    height: 335,
    type: 'area',
    dropShadow: {
      enabled: true,
      color: '#623CEA14',
      top: 10,
      blur: 4,
      left: 0,
      opacity: 0.1,
    },
    toolbar: {
      show: false,
    },
  },
  responsive: [
    {
      breakpoint: 1024,
      options: {
        chart: {
          height: 300,
        },
      },
    },
    {
      breakpoint: 1366,
      options: {
        chart: {
          height: 350,
        },
      },
    },
  ],
  stroke: {
    width: [2, 2],
    curve: 'straight',
  },
  grid: {
    xaxis: {
      lines: {
        show: true,
      },
    },
    yaxis: {
      lines: {
        show: true,
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  markers: {
    size: 4,
    colors: '#fff',
    strokeColors: ['#3056D3', '#80CAEE'],
    strokeWidth: 3,
    strokeOpacity: 0.9,
    strokeDashArray: 0,
    fillOpacity: 1,
    discrete: [],
    hover: {
      size: undefined,
      sizeOffset: 5,
    },
  },
  xaxis: {
    type: 'category',
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  yaxis: {
    title: {
      style: {
        fontSize: '0px',
      },
    },
  },
};

interface SeriesType {
  name: string;
  data: DataPoint[];
}

interface ChartState {
  series: SeriesType[];
}

interface DataPoint {
  x: string;
  y: number;
}

interface SeriesData {
  name: string;
  data: DataPoint[];
}

const LineChartTwo: React.FC = () => {
  const [options, setOptions] = useState<ApexOptions>(baseOptions);
  const [chartState, setChartState] = useState<ChartState>({
    series: [],
  });

  // States for filter options
  const [years, setYears] = useState<string[]>([]);
  const [bodegas, setBodegas] = useState<string[]>([]);
  const [skus, setSkus] = useState<string[]>([]);

  // Selected filters
  const [selectedYear, setSelectedYear] = useState<string[]>([]); // Updated to handle multi-select as array
  const [selectedBodega, setSelectedBodega] = useState<string[]>([]);
  const [selectedSku, setSelectedSku] = useState<string[]>([]);

  const fetchSkusForBodega = async (bodegas: string[]) => {
    if (bodegas.length) {
      const query = new URLSearchParams();
      bodegas.forEach((bodega) => query.append('bodega', bodega));
      fetch(`http://localhost:8000/api/available-skus?${query.toString()}`)
        .then((response) => response.json())
        .then((json) => {
          const skus = json.data;
          setSkus(skus);
          if (skus.length) {
            setSelectedSku([skus[0]]);
          }
        });
    }
  };

  useEffect(() => {
    let ignore = false;
    fetch('http://localhost:8000/api/available-years')
      .then((response) => response.json())
      .then((json) => {
        if (!ignore) {
          const years = json.data;
          setYears(years);
          if (years.length) {
            setSelectedYear([years[0]]);
          }
        }
      });
    return () => {
      ignore = true;
    };
  }, []);

  useEffect(() => {
    let ignore = false;
    fetch('http://localhost:8000/api/available-bodegas')
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

  // Fetch skus for selected bodega only when bodega changes
  useEffect(() => {
    if (selectedBodega.length) {
      fetchSkusForBodega(selectedBodega);
    }
  }, [selectedBodega]); // Fetch skus when selected bodega changes

  // Fetch chart data based on selected filters
  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const query = new URLSearchParams();

        selectedBodega.forEach((bodega) => query.append('bodega', bodega));
        selectedYear.forEach((year) => query.append('anio', year));
        selectedSku.forEach((sku) => query.append('sku', sku));

        const response = await fetch(
          `http://localhost:8000/api/line-chart-2?${query.toString()}`,
        );
        const data = await response.json();
        const series = data.data;

        let allData: number[] = [];

        // Loop through each item in the 'data' array
        series.forEach((item: SeriesData) => {
          // For each item, push all the 'value' fields from the 'data' array into allValues
          item.data.forEach((entry) => {
            allData.push(entry.y);
          });
        });

        // Calculate min and max values for the y-axis dynamically
        const { min, max } = getMinMaxValues(allData);

        setChartState({
          series,
        });

        setOptions({
          ...baseOptions,
          yaxis: {
            ...baseOptions.yaxis,
            min: min,
            max: max,
          },
          xaxis: {
            ...baseOptions.xaxis,
          },
        });
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };

    const shouldFetchChartData =
      selectedYear.length && selectedBodega.length && selectedSku.length;

    if (shouldFetchChartData) {
      fetchChartData();
    }
  }, [selectedYear, selectedSku]); // Fetch data when filters change

  // Convert to react-select format
  const yearOptions = years.map((year) => ({ value: year, label: year }));
  const bodegaOptions = bodegas.map((bodega) => ({
    value: bodega,
    label: bodega,
  }));
  const skuOptions = skus.map((sku) => ({ value: sku, label: sku }));

  return (
    <div className="col-span-12 rounded-sm border border-stroke bg-white px-5 pt-7.5 pb-5 shadow-default dark:border-strokedark dark:bg-boxdark sm:px-7.5 xl:col-span-8">
      <div className="col-span-4 mb-6">
        {/* Year Multi-select */}
        {/* <Select
          isMulti
          value={selectedYear.map(year => ({ value: year, label: year }))}
          // onChange={(e) => setSelectedYear(e ? e.map((option: any) => option.value) : [])}
          onChange={preventDeletion(selectedYear, setSelectedYear)}
          options={yearOptions}
          className="mb-3"
          placeholder="Select Year"
          isClearable={isClearable(selectedYear)} // Disable the "x" for the last element
        /> */}

        {/* Bodega Select */}
        <Select
          value={
            selectedYear.length > 0
              ? { value: selectedYear[0], label: selectedYear[0] }
              : null
          } // Check if there's a selected bodega or set to null
          onChange={(e) => setSelectedYear(e ? [e.value] : [])} // When the value changes, update the selected bodega
          options={yearOptions}
          className="mb-3"
          placeholder="Select Year"
        />

        {/* Bodega Select */}
        <Select
          value={
            selectedBodega.length > 0
              ? { value: selectedBodega[0], label: selectedBodega[0] }
              : null
          } // Check if there's a selected bodega or set to null
          onChange={(e) => setSelectedBodega(e ? [e.value] : [])} // When the value changes, update the selected bodega
          options={bodegaOptions}
          className="mb-3"
          placeholder="Select Bodega"
        />

        {/* SKU Multi-select */}
        <Select
          isMulti
          value={selectedSku.map((sku) => ({ value: sku, label: sku }))}
          // onChange={(e) => setSelectedSku(e ? e.map((option: any) => option.value) : [])}
          onChange={preventDeletion(selectedSku, setSelectedSku)}
          options={skuOptions}
          className="mb-3"
          placeholder="Select SKUs"
          isOptionDisabled={(option) =>
            selectedSku.length >= 4 && !selectedSku.includes(option.value)
          } // Disable options when 4 selections are reached
          isClearable={isClearable(selectedSku)} // Disable the "x" for the last element
        />
      </div>

      <div>
        <ReactApexChart
          options={options}
          series={chartState.series}
          type="area"
          height={350}
        />
      </div>
    </div>
  );
};

export default LineChartTwo;
