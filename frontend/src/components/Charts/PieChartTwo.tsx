import { ApexOptions } from 'apexcharts';
import React, { useState, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';
import Select from 'react-select';

const baseOptions: ApexOptions = {
  legend: {
    show: true,
    horizontalAlign: 'center',
    labels: {
      useSeriesColors: true,
      colors: '#333',
    },
  },
  title: {
    text: 'Distribución de pronósticos',
    align: 'center',
    style: {
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#333',
      fontFamily: 'Satoshi, sans-serif',
    },
  },
  chart: {
    fontFamily: 'Satoshi, sans-serif',
    height: 350,
    type: 'pie',
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    pie: {
      expandOnClick: true,
      donut: {
        size: '70%', // Donut effect (optional)
      },
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
  colors: ['#025E73', '#34675C', '#A5A692', '#F2A71B', '#41134A'],
};

interface PieChartState {
  series: number[];
  labels: string[];
}

interface PieChartResponse {
  data: {
    labels: string[];
    series: number[];
  };
}

const ChartPieTwo: React.FC = () => {
  const [options, setOptions] = useState<ApexOptions>(baseOptions);
  const [chartState, setChartState] = useState<PieChartState>({
    series: [],
    labels: [],
  });
  const [bodegas, setBodegas] = useState<string[]>([]);
  const [selectedBodega, setSelectedBodega] = useState<string[]>([]);

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
      })
      .catch((error) => {
        console.error('Error fetching bodegas:', error);
      });
    return () => {
      ignore = true;
    };
  }, []);

  // Fetch chart data based on selected filters
  useEffect(() => {
    const query = new URLSearchParams();
    selectedBodega.forEach((bodega) => query.append('bodega', bodega));
    fetch(`http://localhost:8000/api/pie-chart-2?${query.toString()}`)
      .then((response) => response.json())
      .then((json: PieChartResponse) => {
        setChartState(json.data);
        setOptions({
          ...baseOptions,
          labels: json.data.labels,
        });
      })
      .catch((error) => {
        console.error('Error fetching pie chart data:', error);
      });
  }, [selectedBodega]);

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
        <ReactApexChart
          options={options}
          series={chartState.series}
          type="pie"
          height={350}
        />
      </div>
    </div>
  );
};

export default ChartPieTwo;
