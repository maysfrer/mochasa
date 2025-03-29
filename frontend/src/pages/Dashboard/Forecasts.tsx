import React from 'react';
import Breadcrumb from '../../components/Breadcrumbs/Breadcrumb';
import LineChartThree from '../../components/Charts/LineChartThree';
import PieChartTwo from '../../components/Charts/PieChartTwo';
import BaseChartTwo from '../../components/Charts/BaseChartTwo';

const Chart: React.FC = () => {
  return (
    <>
      <Breadcrumb pageName="Pronósticos" />

      <div className="grid grid-cols-12 gap- md:gap-6 2xl:gap-7.5">
        <div className="col-span-12">
          <LineChartThree />
        </div>
        <div className="col-span-12">
          <PieChartTwo />
        </div>
        <div className="col-span-12">
          <BaseChartTwo />
        </div>
      </div>
    </>
  );
};

export default Chart;
