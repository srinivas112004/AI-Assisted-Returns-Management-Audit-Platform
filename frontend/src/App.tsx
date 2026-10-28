import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { OrdersPage } from './pages/OrdersPage';
import { ReturnsQueuePage } from './pages/ReturnsQueuePage';
import { ReturnDetailPage } from './pages/ReturnDetailPage';
import { EligibilityAuthPage } from './pages/EligibilityAuthPage';
import { ShipmentsPage } from './pages/ShipmentsPage';
import { InspectionPage } from './pages/InspectionPage';
import { RefundsPage } from './pages/RefundsPage';
import { DispositionsPage } from './pages/DispositionsPage';
import { ExceptionsPage } from './pages/ExceptionsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { GeneratorPage } from './pages/GeneratorPage';
import { ValidationPage } from './pages/ValidationPage';
import { DocumentationPage } from './pages/DocumentationPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="returns" element={<ReturnsQueuePage />} />
          <Route path="returns/:rmaNumber" element={<ReturnDetailPage />} />
          <Route path="eligibility" element={<EligibilityAuthPage />} />
          <Route path="shipments" element={<ShipmentsPage />} />
          <Route path="inspections" element={<InspectionPage />} />
          <Route path="refunds" element={<RefundsPage />} />
          <Route path="dispositions" element={<DispositionsPage />} />
          <Route path="exceptions" element={<ExceptionsPage />} />
          <Route path="audit" element={<ExceptionsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="generator" element={<GeneratorPage />} />
          <Route path="validation" element={<ValidationPage />} />
          <Route path="documentation" element={<DocumentationPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
