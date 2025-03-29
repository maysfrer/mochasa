import React from 'react';
import Breadcrumb from '../../components/Breadcrumbs/Breadcrumb';
import PieChartThree from '../../components/Charts/PieChartThree';
import BaseChartThree from '../../components/Charts/BaseChartThree';
import BaseChartFour from '../../components/Charts/BaseChartFour';
import BaseChartFive from 'src/components/Charts/BaseChartFive';

const Chart: React.FC = () => {
  return (
    <>
      <Breadcrumb pageName="Políticas de inventario" />

      <div className="grid grid-cols-12 gap- md:gap-6 2xl:gap-7.5">
        <div className="col-span-12">
          <BaseChartThree />
        </div>
        <div className="col-span-12">
          <BaseChartFour />
        </div>
        <div className="col-span-12">
          <BaseChartFive />
        </div>
        <div className="col-span-12">
          <PieChartThree />
        </div>
      </div>
    </>
  );
};

export default Chart;
