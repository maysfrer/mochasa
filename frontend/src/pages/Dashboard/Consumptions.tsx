import React from 'react';
import Breadcrumb from '../../components/Breadcrumbs/Breadcrumb';
import LineChartTwo from '../../components/Charts/LineChartTwo';
import PieChartOne from '../../components/Charts/PieChartOne';
import LineChartOne from '../../components/Charts/LineChartOne';

const Consumptions: React.FC = () => {
  return (
    <>
      <Breadcrumb pageName="Consumos" />

      <div className="mt-4 grid grid-cols-12 gap-4 md:mt-6 md:gap-6 2xl:mt-7.5 2xl:gap-7.5">
        <div className="col-span-12">
          <LineChartOne />
        </div>

        <div className="col-span-12">
          <LineChartTwo />
        </div>

        <div className="col-span-12">
          <PieChartOne />
        </div>
      </div>
    </>
  );
};

export default Consumptions;
