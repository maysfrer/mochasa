import { useEffect, useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';

import Loader from './common/Loader';
import PageTitle from './components/PageTitle';
import DefaultLayout from './layout/DefaultLayout';
import Consumptions from './pages/Dashboard/Consumptions';
import Forecasts from './pages/Dashboard/Forecasts';
import InventoryPolicies from './pages/Dashboard/InventoryPolicies';

function App() {
  const [loading, setLoading] = useState<boolean>(true);
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  useEffect(() => {
    setTimeout(() => setLoading(false), 1000);
  }, []);

  return loading ? (
    <Loader />
  ) : (
    <DefaultLayout>
      <Routes>
        {/* <Route
          index
          element={
            <>
              <PageTitle title="Dashboard | Gestión de Inventario" />
              <Dashboard />
            </>
          }
        /> */}
        <Route
          path="/dashboard/consumptions"
          element={
            <>
              <PageTitle title="Consumos | Gestión de Inventario" />
              <Consumptions />
            </>
          }
        />
        <Route
          path="/dashboard/forecasts"
          element={
            <>
              <PageTitle title="Pronósticos | Gestión de Inventario" />
              <Forecasts />
            </>
          }
        />
        <Route
          path="/dashboard/inventory-policies"
          element={
            <>
              <PageTitle title="Políticas de Inventario | Gestión de Inventario" />
              <InventoryPolicies />
            </>
          }
        />
      </Routes>
    </DefaultLayout>
  );
}

export default App;
