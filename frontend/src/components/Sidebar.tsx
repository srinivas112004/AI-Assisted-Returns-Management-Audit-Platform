import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ShoppingCart,
  RotateCcw,
  CheckCircle2,
  Truck,
  ClipboardCheck,
  CreditCard,
  Boxes,
  AlertTriangle,
  History,
  BarChart3,
  FileCheck,
  Database,
  BookOpen,
} from 'lucide-react';

interface NavItem {
  name: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
}

const operationalNav: NavItem[] = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Orders Explorer', to: '/orders', icon: ShoppingCart },
  { name: 'Returns Queue', to: '/returns', icon: RotateCcw },
  { name: 'Eligibility & Auth', to: '/eligibility', icon: CheckCircle2 },
  { name: 'Warehouse Shipments', to: '/shipments', icon: Truck },
  { name: 'Inspection Bay', to: '/inspections', icon: ClipboardCheck },
  { name: 'Refunds & Payouts', to: '/refunds', icon: CreditCard },
  { name: 'Inventory Disposition', to: '/dispositions', icon: Boxes },
];

const auditNav: NavItem[] = [
  { name: 'Exceptions & Monitor', to: '/exceptions', icon: AlertTriangle },
  { name: 'Audit Event Log', to: '/audit', icon: History },
  { name: 'Analytics & Metrics', to: '/analytics', icon: BarChart3 },
  { name: 'Validation Engine', to: '/validation', icon: FileCheck },
];

const systemNav: NavItem[] = [
  { name: 'Data Generator', to: '/generator', icon: Database },
  { name: 'Data Dictionary & Docs', to: '/documentation', icon: BookOpen },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-100 gap-3">
        <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
          Y
        </div>
        <div>
          <span className="font-semibold text-slate-900 text-sm tracking-tight block">Yotaa AI</span>
          <span className="text-[11px] text-slate-500 block leading-tight font-medium">Returns & Audit Platform</span>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <p className="px-3 text-[10px] font-semibold text-slate-600 tracking-wider uppercase mb-2">
            Operations
          </p>
          <div className="space-y-0.5">
            {operationalNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>

        <div>
          <p className="px-3 text-[10px] font-semibold text-slate-600 tracking-wider uppercase mb-2">
            Audit & Intelligence
          </p>
          <div className="space-y-0.5">
            {auditNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>

        <div>
          <p className="px-3 text-[10px] font-semibold text-slate-600 tracking-wider uppercase mb-2">
            Governance & Specs
          </p>
          <div className="space-y-0.5">
            {systemNav.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`
                }
              >
                <item.icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[11px] font-medium text-slate-600">Engine Online</span>
          <span className="ml-auto text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono font-medium">
            v1.0
          </span>
        </div>
      </div>
    </aside>
  );
};
